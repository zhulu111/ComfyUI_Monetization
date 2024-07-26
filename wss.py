_b='crystools.monitor'
_a='uniqueid'
_Z='crystools.bind'
_Y='videos'
_X='prompt'
_W='images'
_V='.json'
_U='send'
_T='crystools.prompt_error'
_S='client_id'
_R=False
_Q='status'
_P='queue_pending'
_O='queue_running'
_N='msg'
_M='text'
_L='filename'
_K='str'
_J='code'
_I='jilu_id'
_H='conn_identifier'
_G='k'
_F='v'
_E=None
_D=True
_C='prompt_id'
_B='data'
_A='type'
import asyncio,hashlib,json,os,queue,random,time,traceback,urllib,uuid,aiohttp,urllib.request,urllib.parse,collections
from concurrent.futures import ThreadPoolExecutor
from threading import Lock,Condition
import websockets,threading
from.public import get_output,write_json_to_file,read_json_from_file,get_address,get_port,generate_unique_client_id,get_port_from_cmdline,args,find_project_root,get_token,get_workflow
os.environ['http_proxy']=''
os.environ['https_proxy']=''
os.environ['no_proxy']='*'
SERVER_1_URI='wss://tt.9syun.com/wss'
ADDRESS=get_address()
PORT=get_port_from_cmdline()
HTTP_ADDRESS='http://{}:{}/'.format(ADDRESS,PORT)
new_client_w_id=f"{str(uuid.uuid4())}:{get_port()}"
SERVER_2_URI='ws://{}:{}/ws?clientId={}'.format(ADDRESS,PORT,new_client_w_id)
RECONNECT_DELAY=1
MAX_RECONNECT_DELAY=3
task_queue_1=queue.Queue()
task_queue_2=queue.Queue()
task_queue_3={}
websocket_queue=collections.deque()
websocket_conn1=_E
websocket_conn2=_E
websocket_conn3=_E
history_data={_O:[],_P:[]}
history_prompt_ids=[]
class MonitoredThreadPoolExecutor(ThreadPoolExecutor):
	def __init__(self,max_workers=_E,thread_name_prefix=''):super().__init__(max_workers=max_workers,thread_name_prefix=thread_name_prefix);self._lock=Lock();self._condition=Condition(self._lock);self._active_tasks=0;self._max_workers=max_workers
	def submit(self,fn,*args,**kwargs):
		with self._lock:
			while self._active_tasks>=self._max_workers:self._condition.wait()
			self._active_tasks+=1
		future=super().submit(self._wrap_task(fn),*args,**kwargs);return future
	def _wrap_task(self,fn):
		def wrapped_fn(*args,**kwargs):
			try:return fn(*args,**kwargs)
			finally:
				with self._lock:self._active_tasks-=1;self._condition.notify_all()
		return wrapped_fn
	def active_tasks(self):
		with self._lock:return self._active_tasks
executor=MonitoredThreadPoolExecutor(max_workers=20)
def print_exception_in_chinese(e):
	'\n    打印异常信息，包括文件名、行号、函数名和错误信息，全部使用中文描述。\n    :param e: 异常对象\n    ';tb=traceback.extract_tb(e.__traceback__)
	if tb:filename,line_number,function_name,text=tb[-1];traceback.print_exception(type(e),e,e.__traceback__)
	else:0
async def websocket_connect(uri,conn_identifier):
	global websocket_conn1,websocket_conn2,send_time;reconnect_delay=RECONNECT_DELAY
	while _D:
		try:
			async with websockets.connect(uri)as websocket:
				print(f"{conn_identifier} 连接成功")
				if conn_identifier==1:websocket_conn1=websocket
				else:
					websocket_conn2=websocket
					for(key,val)in task_queue_3.items():
						is_set=key in history_prompt_ids
						if is_set:0
						else:task_queue_2.put({_A:_U,_C:key})
				reconnect_delay=RECONNECT_DELAY;tasks=[asyncio.create_task(receive_messages(websocket,conn_identifier)),asyncio.create_task(send_heartbeat())];await asyncio.gather(*tasks)
		except websockets.ConnectionClosedError as e:print_exception_in_chinese(e);await asyncio.sleep(reconnect_delay)
		except websockets.ConnectionClosedOK as e:print_exception_in_chinese(e);await asyncio.sleep(reconnect_delay)
		except Exception as e:await asyncio.sleep(reconnect_delay)
		reconnect_delay=min(reconnect_delay*2,MAX_RECONNECT_DELAY)
def get_history_prompt(prompt_id):
	try:
		if websocket_conn2 is not _E and websocket_conn2.open:
			with urllib.request.urlopen(HTTP_ADDRESS+'history'+'/'+prompt_id)as response:return json.loads(response.read())
		else:return{}
	except Exception as e:print(f"[91m 服务正在连接中{get_time()}  [0m");return{}
async def getHistoryPrompt(prompt_id,type_a=''):
	A='ok';result_data=[{_A:_K,_G:_C,_F:prompt_id}];result=get_history_prompt(prompt_id);response_status=_E
	try:
		if prompt_id in result:
			result=result[prompt_id];status=result.get(_Q,{})
			if status.get('completed',_R):
				result_data.append({_A:_K,_G:A,_F:'1'})
				for output in result.get('outputs',{}).values():
					for media in[_W,'gifs',_Y]:
						if media in output:
							for item in output[media]:
								if _L in item:result_data.append({_A:_W,_G:'file',_F:(args.output_directory if args.output_directory else find_project_root()+'output')+'/'+item[_L]})
			else:result_data.append({_A:_K,_G:A,_F:'0',_M:'completed状态不对'})
		else:
			is_set=prompt_id in history_prompt_ids
			if is_set:return
			result_data.append({_A:_K,_G:A,_F:'0',_M:'prompt_id没有找到'})
		response_status=200
	except Exception as e:print_exception_in_chinese(e);result_data.append({_A:_K,_G:A,_F:'0',_M:'异常的信息'});response_status=500
	submit_url='https://tt.9syun.com/app/index.php?i=66&t=0&v=1.0&from=wxapp&tech_client=tt&tech_scene=990001&c=entry&a=wxapp&do=ttapp&r=comfyui.resultv2.formSubmitForComfyUi&m=tech_huise';connector=aiohttp.TCPConnector()
	async with aiohttp.ClientSession(connector=connector)as session:
		try:form_res_data=await send_form_data(session,submit_url,result_data,prompt_id)
		except json.JSONDecodeError as e:print_exception_in_chinese(e);result_data.append({_A:_K,_G:A,_F:'0',_M:'json异常的信息'});response_status=400
		except Exception as e:print_exception_in_chinese(e);result_data.append({_A:_K,_G:A,_F:'0',_M:'aiohttpException异常的信息'});response_status=500
		finally:
			if'session'in locals():await session.close()
		return{_Q:response_status,'message':'操作完成.'if response_status==200 else'发生错误.'}
async def send_form_data(session,url,data,prompt_id=_E):
	A='application/octet-stream';global websocket_conn1;form_data=aiohttp.FormData()
	try:
		for item in data:
			if item[_A]==_K:form_data.add_field(item[_G],item[_F])
			if item[_A]==_W or item[_A]=='gifs'or item[_A]==_Y or item[_A]=='files':
				if os.path.exists(item[_F]):
					with open(item[_F],'rb')as f:file_content=f.read()
					form_data.add_field(item[_G]+'[]',file_content,filename=os.path.basename(item[_F]),content_type=A)
				else:0
			if item[_A]=='file':
				if os.path.exists(item[_F]):
					with open(item[_F],'rb')as f:file_content=f.read()
					form_data.add_field(item[_G],file_content,filename=os.path.basename(item[_F]),content_type=A)
				else:0
	except Exception as e:print_exception_in_chinese(e)
	async with session.post(url,data=form_data)as response:
		if response.status==200:
			resp_text=await response.text()
			if prompt_id and websocket_conn1 is not _E and websocket_conn1.open==_D:websocket_queue.append({_H:1,_B:{_A:'crystools.executed_success',_B:{_C:prompt_id}}})
			return resp_text
		else:return
async def server1_receive_messages(websocket,message_type,message_json):
	if message_type=='init':await websocket.send(json.dumps({_A:_Z,_B:{_S:new_client_w_id}}))
	if message_type==_X:
		prompt_data=message_json[_B];jilu_id=prompt_data[_I];uniqueid=message_json[_a];output=get_output(uniqueid+_V);workflow=get_workflow(uniqueid+_V)
		if output:executor.submit(run_async_task,output,prompt_data,workflow,jilu_id)
		elif websocket.open:websocket_queue.append({_H:1,_B:{_A:_T,_B:{_I:jilu_id,_N:'作品工作流找不到了'}}})
def optimized_process_history_data(history_data_1):
	running=[];pending=[]
	if history_data_1:
		queue_running=history_data_1.get(_O,[])
		if queue_running:running.append(queue_running[0][1])
		queue_pending=history_data_1.get(_P,[])
		if queue_pending:pending=sorted(queue_pending,key=lambda x:int(x[0]));pending=[item[1]for item in pending]
	return running,pending
async def server2_receive_messages(websocket,message_type,message_json):
	B='queue_remaining';A='exec_info';global send_time
	if message_type and message_type!=_b:
		if message_type==_Q and message_json[_B][_Q][A]:websocket_queue.append({_H:1,_B:{_A:'crystools.queue',_B:{_S:new_client_w_id,B:message_json[_B][_Q][A][B]}}});await send_heartbeat_to_server2()
		if message_type=='execution_start':0
		if message_type=='executing':0
		if message_type=='execution_error':task_queue_2.put({_A:_U,_C:message_json[_B][_C]})
		if message_type=='executed':task_queue_2.put({_A:_U,_C:message_json[_B][_C]})
		if message_type=='progress':0
		if message_type=='execution_cached'and _C in message_json[_B]:task_queue_2.put({_A:_U,_C:message_json[_B][_C]})
async def receive_messages(websocket,conn_identifier):
	'接收消息的异步任务'
	if websocket.open:
		try:
			async for message in websocket:
				if type(message)!=bytes:
					message_dict=json.loads(message);message_type=message_dict.get(_A)
					if conn_identifier==1:await server1_receive_messages(websocket,message_type,message_dict)
					elif conn_identifier==2:await server2_receive_messages(websocket,message_type,message_dict)
		except json.JSONDecodeError as e:print_exception_in_chinese(e)
		finally:await asyncio.sleep(.5)
async def send_heartbeat():
	'发送心跳的异步任务'
	while _D:
		try:
			if websocket_conn1 is not _E and websocket_conn1.open==_D and websocket_conn2 is not _E and websocket_conn2.open==_D:await send_heartbeat_to_server2()
		except Exception as e:print_exception_in_chinese(e)
		finally:await asyncio.sleep(10)
def get_history():
	global last_get_history_time
	try:
		if websocket_conn2 is not _E and websocket_conn2.open==_D:
			last_get_history_time=time.time()
			with urllib.request.urlopen(HTTP_ADDRESS+'queue')as response:return json.loads(response.read())
		else:return{_O:[],_P:[]}
	except Exception as e:return{_O:[],_P:[]}
def get_filenames(directory):
	if os.path.exists(directory):all_entries=os.listdir(directory);all_entries=[name for name in all_entries if os.path.isfile(os.path.join(directory,name))];all_entries=[name.split('.')[0]for name in all_entries];return all_entries
	else:return[]
send_time='0'
def get_time():return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
async def send_heartbeat_to_server2():
	running,pending=optimized_process_history_data(history_data)
	try:file_names=get_filenames(find_project_root()+'custom_nodes/ComfyUI_Monetization/config/json/api/');websocket_queue.append({_H:1,_B:{_A:_b,_B:{'files':file_names,'running':running,'pending':pending,_S:new_client_w_id}}})
	except Exception as e:print_exception_in_chinese(e)
def run_task_in_loop(task,*args,**kwargs):
	'在死循环中运行任务'
	while _D:task(*args,**kwargs);time.sleep(1)
loop_num=0
async def run_websocket_task_in_loop():
	global loop_num
	while _D:
		try:
			if len(websocket_queue)>0:
				websocket_info=websocket_queue.popleft()
				if _H in websocket_info:
					if websocket_conn3 is not _E and websocket_conn3.open and websocket_conn1 is not _E and websocket_conn1.open:
						websocket_info[_B]['zhu_client_id']=new_client_w_id
						if websocket_info[_H]==1:await websocket_conn3.send(json.dumps(websocket_info[_B]))
			else:
				loop_num=loop_num+1
				if loop_num>100:loop_num=0;await websocket_conn3.send(json.dumps({'time':get_time()}))
		except Exception as e:break
		finally:await asyncio.sleep(.02)
def generate_md5_uid_timestamp_filename(original_filename):'\n    生成一个MD5加密后的唯一文件名，包含原始文件名、时间戳和随机数。\n\n    参数:\n    original_filename (str): 原始文件名。\n\n    返回:\n    str: MD5加密后的唯一文件名。\n    ';timestamp=str(time.time());random_number=str(generate_large_random_number(32));combined_string=original_filename+timestamp+random_number;md5_hash=hashlib.md5(combined_string.encode('utf-8')).hexdigest();file_extension=os.path.splitext(original_filename)[1];filename=md5_hash+file_extension;return filename
async def loca_download_image(url,filename):
	"\n    同步下载网络图片并保存到本地。\n\n    :param url: 图片的URL\n    :param filename: 保存到本地的文件名\n    :param dir_name: 保存图片的目录，默认为'input'\n    ";dir_name=find_project_root()+'input';no_proxy_handler=urllib.request.ProxyHandler({});opener=urllib.request.build_opener(no_proxy_handler);file_new_name=generate_md5_uid_timestamp_filename(filename)
	try:
		response=opener.open(url)
		if response.getcode()==200:
			full_path=os.path.join(dir_name,file_new_name)
			if os.path.exists(full_path):return{_J:_D,_L:file_new_name}
			with open(full_path,'wb')as f:f.write(response.read())
			return{_J:_D,_L:file_new_name}
		else:return{_J:_R,_L:file_new_name}
	except Exception as e:return{_J:_R,_L:file_new_name}
def generate_large_random_number(num_bits):'\n    生成一个指定位数的随机大数。\n\n    参数:\n    num_bits (int): 随机数的位数。\n\n    返回:\n    int: 指定位数的随机大数。\n    ';return random.getrandbits(num_bits)
def queue_prompt(prompt,workflow,new_client_id):
	A='extra_data'
	try:
		if websocket_conn2 is not _E and websocket_conn2.open:p={_X:prompt,_S:new_client_id,A:workflow[A]};data=json.dumps(p).encode('utf-8');req=urllib.request.Request(HTTP_ADDRESS+_X,data=data);return json.loads(urllib.request.urlopen(req).read())
		else:return{}
	except Exception as e:print_exception_in_chinese(e);return{}
async def process_json_elements(json_data,prompt_data,workflow,jilu_id):
	J='node_errors';I='发送指令失败3';H='video';G='image';F='cs_texts';E='cs_videos';D='cs_imgs';C='upImage';B='node';A='inputs';global websocket_conn1
	try:
		if D in prompt_data and prompt_data[D]:
			for item in prompt_data[D]:
				filename=os.path.basename(item[C]);download_info=await loca_download_image(item[C],filename);download_status=download_info[_J];file_new_name=download_info[_L]
				if download_status==_R:raise Exception('图片下载失败')
				if str(item[B])in json_data and A in json_data[str(item[B])]and G in json_data[str(item[B])][A]:json_data[str(item[B])][A][G]=file_new_name
		if E in prompt_data and prompt_data[E]:
			for item in prompt_data[E]:
				filename=os.path.basename(item[C]);download_info=await loca_download_image(item[C],filename);download_status=download_info[_J];file_new_name=download_info[_L]
				if download_status==_R:raise Exception('视频下载失败')
				if str(item[B])in json_data and A in json_data[str(item[B])]and H in json_data[str(item[B])][A]:json_data[str(item[B])][A][H]=file_new_name
		if F in prompt_data and prompt_data[F]:
			for item in prompt_data[F]:json_data[str(item[B])][A][_M]=item['value']
	except KeyError as e:print_exception_in_chinese(e);websocket_queue.appendleft({_H:1,_B:{_A:_T,_B:{_I:jilu_id,_N:'发送指令失败1'}}});return{_J:0,_I:jilu_id}
	except Exception as e:print_exception_in_chinese(e);websocket_queue.appendleft({_H:1,_B:{_A:_T,_B:{_I:jilu_id,_N:'发送指令失败2'}}});return{_J:0,_I:jilu_id}
	async def print_item(key,value):
		C='class_type';B='crf'
		try:
			if value[C]=='KSampler'and A in json_data[key]:json_data[key][A]['seed']=generate_large_random_number(15)
			if value[C]=='VHS_VideoCombine'and A in json_data[key]and B in json_data[key][A]:
				if json_data[key][A][B]==0:json_data[key][A][B]=1
		except Exception as e:print_exception_in_chinese(e);websocket_queue.appendleft({_H:1,_B:{_A:_T,_B:{_I:jilu_id,_N:I}}})
	tasks=[print_item(key,value)for(key,value)in json_data.items()];await asyncio.gather(*tasks)
	try:
		result=queue_prompt(json_data,workflow,new_client_w_id)
		if J in result:
			if result[J]:raise Exception('发送指令失败')
		try:websocket_queue.appendleft({_H:1,_B:{_A:'crystools.prompt_ok',_B:{_C:result[_C],_I:jilu_id,_N:'发送指令成功'}}})
		except Exception as e:print_exception_in_chinese(e)
		task_queue_3[result[_C]]={_I:jilu_id};return{_J:1,_C:result[_C]}
	except Exception as e:print_exception_in_chinese(e);websocket_queue.appendleft({_H:1,_B:{_A:_T,_B:{_I:jilu_id,_N:I}}});return{_J:0,_C:jilu_id}
def run_async_task(json_data,prompt_data,workflow,jilu_id):return asyncio.run(process_json_elements(json_data,prompt_data,workflow,jilu_id))
def run_async_task2(prompt_id):asyncio.run(getHistoryPrompt(prompt_id))
def task_3():
	'消费任务队列的任务'
	while _D:
		try:
			task_info=task_queue_1.get();output=get_output(task_info[_a]+_V)
			if output:executor.submit(run_async_task,output,task_info['prompt_data'],task_info[_I])
			task_queue_1.task_done()
		except Exception as e:print_exception_in_chinese(e)
		finally:time.sleep(1)
def task_4():
	global history_data;'消费来自连接 2 的任务队列的任务'
	while _D:
		try:
			task_info=task_queue_2.get()
			if _C in task_info:history_data=get_history();preprocess_history_data(history_data);task_queue_3.pop(task_info[_C],_E);executor.submit(run_async_task2,task_info[_C]);task_queue_2.task_done()
		except Exception as e:print_exception_in_chinese(e)
		finally:time.sleep(.1)
def print_thread_status():
	'打印所有活动线程的状态'
	while _D:
		print('\n当前活动线程:')
		for thread in threading.enumerate():print(f"线程名: {thread.name}, 线程ID: {thread.ident}, 活动状态: {thread.is_alive()}")
		time.sleep(5)
def main_task():
	'主线程的任务'
	for i in range(10):time.sleep(1)
def websocket_thread(uri,conn_identifier):loop=asyncio.new_event_loop();asyncio.set_event_loop(loop);loop.run_until_complete(websocket_connect(uri,conn_identifier))
def websocket_thread_fu(uri,conn_identifier):loop=asyncio.new_event_loop();asyncio.set_event_loop(loop);loop.run_until_complete(websocket_connect_fu(uri,conn_identifier))
def preprocess_history_data(history_data):
	global history_prompt_ids;'\n    预处理 history_data，将所有 prompt_id 存储在集合中。\n\n    :param history_data: 包含 queue_running 和 queue_pending 的历史数据\n    :return: 包含所有 prompt_id 的集合\n    ';prompt_ids=set()
	if history_data is _E:history_prompt_ids=prompt_ids;return
	for queue in[_O,_P]:
		for item in history_data.get(queue,[]):prompt_ids.add(item[1])
	history_prompt_ids=prompt_ids
last_get_history_time=0
async def task5():
	global history_data
	while _D:
		try:history_data=get_history();preprocess_history_data(history_data)
		except Exception as e:print_exception_in_chinese(e)
		await asyncio.sleep(1)
def task5_thread():loop=asyncio.new_event_loop();asyncio.set_event_loop(loop);loop.run_until_complete(task5())
def start_async_task_in_thread(async_func):'\n    在新线程中启动一个事件循环并运行异步任务\n    ';loop=asyncio.new_event_loop();asyncio.set_event_loop(loop);loop.run_until_complete(async_func())
async def websocket_connect_fu(uri,conn_identifier):
	global websocket_conn3;reconnect_delay=RECONNECT_DELAY
	while _D:
		try:
			async with websockets.connect(uri)as websocket:print(f"{conn_identifier} 连接成功");websocket_conn3=websocket;await websocket_conn3.send(json.dumps({_A:_Z,_B:{_S:new_client_w_id+'_fu'}}));reconnect_delay=RECONNECT_DELAY;tasks=[asyncio.create_task(run_websocket_task_in_loop())];await asyncio.gather(*tasks)
		except websockets.ConnectionClosedError as e:print(f"[91m 3 服务正在连接中{get_time()}  [0m");await asyncio.sleep(reconnect_delay)
		except websockets.ConnectionClosedOK as e:await asyncio.sleep(reconnect_delay)
		except Exception as e:await asyncio.sleep(reconnect_delay)
		reconnect_delay=min(reconnect_delay*2,MAX_RECONNECT_DELAY)
def thread_run():threading.Thread(target=websocket_thread,args=(SERVER_1_URI,1),daemon=_D).start();threading.Thread(target=websocket_thread,args=(SERVER_2_URI,2),daemon=_D).start();threading.Thread(target=websocket_thread_fu,args=(SERVER_1_URI,3),daemon=_D).start();threading.Thread(target=task5_thread).start();executor.submit(run_task_in_loop,task_4)
async def update_worker_flow(uniqueid,data,flow_type='api/'):write_json_to_file(data,uniqueid+_V,'json/'+flow_type,'json')