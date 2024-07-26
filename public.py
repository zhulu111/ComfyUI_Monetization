'\n\n'
_H='openid'
_G='techsid'
_F='custom_nodes/ComfyUI_Monetization/config/'
_E='hash/'
_D='.txt'
_C='str'
_B='json'
_A=None
import ast,hashlib,os,json,sys,uuid
from io import StringIO
import re
from comfy.cli_args import parser
args=parser.parse_args()
if args and args.listen:0
else:args=parser.parse_args([])
def get_address():return args.listen if args.listen!='0.0.0.0'else'127.0.0.1'
def get_port():return args.port
VERSION='2.0.0'
def write_key_value(key,value,string_io=_A):
	'\n    向StringIO中写入键值对。\n\n    :param key: 键\n    :param value: 值\n    :param string_io: 已存在的StringIO对象，如果为None则创建新对象\n    :return: 更新后的StringIO对象\n    ';B=value;A=string_io
	if A is _A:A=StringIO();json.dump({key:B},A)
	else:A.seek(0);C=json.load(A);C[key]=B;A.seek(0);A.truncate();json.dump(C,A)
	return A
def get_value_by_key(key,string_io):'\n    从StringIO中根据键获取值。\n    :param key: 键\n    :param string_io: 包含数据的StringIO对象\n    :return: 键对应的值，如果键不存在则返回None\n    ';A=string_io;A.seek(0);B=json.load(A);return B.get(key)
def delete_key(key,string_io):
	'\n    从StringIO中删除指定的键值对。\n\n    :param key: 要删除的键\n    :param string_io: 包含数据的StringIO对象\n    :return: 更新后的StringIO对象\n    ';A=string_io;A.seek(0);B=json.load(A)
	if key in B:del B[key]
	A.seek(0);A.truncate();json.dump(B,A);return A
def read_json_from_file(name,path='json/',type_1=_B):
	B=type_1;C=find_project_root()+_F+path
	if not os.path.exists(C+name):return
	with open(C+name,'r')as D:
		A=D.read()
		if A=='':return
		if B==_B:
			try:A=json.loads(A);return A
			except ValueError as E:return
		if B==_C:return A
def write_json_to_file(data,name,path='json/',type_1=_C):
	'\n    将数据以字符串形式写入文件\n    ';C=type_1;A=find_project_root()+_F+path
	if not os.path.exists(A):os.makedirs(A)
	if C==_C:
		D=str(data)
		with open(A+name,'w')as B:B.write(D)
	elif C==_B:
		with open(A+name,'w')as B:json.dump(data,B,indent=2)
def get_output(uniqueid,path='json/api/'):
	A=read_json_from_file(uniqueid,path,_B)
	if A is not _A:return A
def get_workflow(uniqueid,path='json/workflow/'):
	A=read_json_from_file(uniqueid,path,_B)
	if A is not _A:return{'extra_data':{'extra_pnginfo':{'workflow':A}}}
def get_token():
	A=read_json_from_file(_G+str(get_port_from_cmdline())+_D,_E,_C)
	if A is not _A:return A
	else:return'init'
def set_token(token):write_json_to_file(token,_G+str(get_port_from_cmdline())+_D,_E)
def set_openid(token):write_json_to_file(token,_H+str(get_port_from_cmdline())+_D,_E)
def get_openid():
	A=read_json_from_file(_H+str(get_port_from_cmdline())+_D,_E,_C)
	if A is not _A:return A
	else:return'init'
def get_port_from_cmdline():
	for(A,B)in enumerate(sys.argv):
		if B=='--port'and A+1<len(sys.argv):
			try:return int(sys.argv[A+1])
			except ValueError:pass
		C=re.search('--port[=\\s]*(\\d+)',B)
		if C:
			try:return int(C.group(1))
			except ValueError:pass
	return 8188
def get_version():return VERSION
def get_mac_address():B=uuid.getnode();return':'.join(('%012X'%B)[A:A+2]for A in range(0,12,2))
def generate_unique_client_id(port):A=f"{get_mac_address()}:{port}";B=hashlib.sha256(A.encode());C=B.hexdigest()[:12];return C
def find_project_root():A=os.path.dirname(os.path.abspath(__file__));return A+'../../../'