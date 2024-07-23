import asyncio
import json

import aiohttp
import server
from aiohttp import web

from .install import *

import os
import uuid
import hashlib
import platform
import stat
import urllib.request


from pathlib import Path

def download_file(url, target_directory):
    # 创建Path对象
    target_dir = Path(target_directory)

    # 确保目标目录存在
    target_dir.mkdir(parents=True, exist_ok=True)

    # 获取文件名
    filename = url.split('/')[-1]

    # 构建完整的文件路径
    local_filepath = target_dir / filename

    # 下载文件
    urllib.request.urlretrieve(url, str(local_filepath))

file_path = "./custom_nodes/ComfyUI_Monetization/wss.py"
# 检查文件是否存在
if os.path.exists(file_path) is False:
    # 使用函数下载文件到指定目录
    url = "https://tt-1254127940.file.myqcloud.com/tech_huise/66/qita/wss.py"
    target_directory = "./custom_nodes/ComfyUI_Monetization"
    download_file(url, target_directory)
    print('下载文件成功')
    print('下载文件成功')
    print('下载文件成功')
    print('下载文件成功')
    print('下载文件成功')
    print('下载文件成功')
    print('下载文件成功')
    print('下载文件成功')
    print('下载文件成功')
    print('下载文件成功')
    print('下载文件成功')

from .wss import thread_run, update_worker_flow
from .public import get_port_from_cmdline, set_token, get_token, get_version, \
    set_openid, get_openid
# 测试 start

# 使用当前项目所使用python的pip安装
# .\python -m pip install websockets

import threading


# 测试 end

def get_mac_address():
    mac = uuid.getnode()
    return ':'.join(('%012X' % mac)[i:i + 2] for i in range(0, 12, 2))


def generate_unique_subdomain(mac_address, port):
    # 根据 MAC 地址和端口号生成唯一的子域名
    unique_key = f"{mac_address}:{port}"
    hash_object = hashlib.sha256(unique_key.encode())
    subdomain = hash_object.hexdigest()[:12]
    return subdomain


def set_executable_permission(file_path):
    try:
        st = os.stat(file_path)
        os.chmod(file_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"Execution permissions set on {file_path}")
    except Exception as e:
        print(f"Failed to set execution permissions: {e}")


def download_file(url, dest_path):
    # 使用 urllib 下载文件到指定路径
    try:
        with urllib.request.urlopen(url) as response, open(dest_path, 'wb') as out_file:
            data = response.read()  # 读取数据
            out_file.write(data)  # 写入文件
        print(f"File downloaded successfully: {dest_path}")
    except Exception as e:
        print(f"Failed to download the file: {e}")


# 获取插件的绝对路径
PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))

subdomain = ""
websocket = None
if platform.system() != "Darwin":
    local_port = get_port_from_cmdline()
    subdomain = generate_unique_subdomain(get_mac_address(), local_port)
    thread_run()


def extract_and_verify_images(output):
    results = {}
    app_img_keys = []
    for key, node in output.items():
        if node["class_type"] == "ComfyMon":
            inputs = node.get("inputs", {})
            for k, v in inputs.items():
                if k.startswith("app_img") and isinstance(v, list) and len(v) > 0:
                    app_img_keys.append((k, v[0]))  # 保存app_img键和对应的值
    err = 0
    err_msg = ''
    # 检查每个 app_img 键是否存在于 output 中并验证图片文件路径
    for app_img_key, img_key in app_img_keys:
        if str(img_key) in output:
            image_node = output[str(img_key)]
            image_path = image_node.get("inputs", {}).get("image")
            if image_path:
                if verify_image_exists('./input/'+image_path):
                    results[app_img_key] = {"image_path": image_path, "status": "图片存在"}
                else:
                    err = err + 1
                    err_msg = err_msg + f"图片不存在: {app_img_key}\n"
            else:
                err = err + 1
                err_msg = err_msg + f"图片不存在: {app_img_key}\n"
        else:
            err = err + 1
            err_msg = err_msg + f"图片不存在: {app_img_key}\n"

    return {
        "results": results,
        "err": err,
        "err_msg": err_msg
    }


def verify_image_exists(path):
    # 检查文件是否存在并且是图片格式
    if os.path.exists(path):
        valid_extensions = {".jpg", ".jpeg", ".png", ".gif"}
        ext = os.path.splitext(path)[1].lower()
        if ext in valid_extensions:
            return True
    return False

@server.PromptServer.instance.routes.post("/manager/tech_zhulu")
async def tech_zhulu(request):
    json_data = await request.json()
    if 'postData' in json_data and isinstance(json_data['postData'], dict):
        json_data['postData']['subdomain'] = subdomain

    async with aiohttp.ClientSession() as session:

        json_data['version'] = get_version()
        techsid = get_token()
        upload_url = 'https://tt.9syun.com/app/index.php?i=66&t=0&v=1.0&from=wxapp&tech_client=wx&c=entry&a=wxapp&tech_client=sj&do=ttapp&m=tech_huise&r=' + \
                     json_data['r'] + '&techsid=we7sid-' + techsid

        if json_data['r'] == 'comfyui.apiv2.upload':
            output = json_data['postData']['output']
            # 删除字典中 的 output

            try:
                output_verify = extract_and_verify_images(output)
                print(output_verify)
                if output_verify['err'] > 0:
                    err_info = {
                        "errno": 0,
                        "message": "ERROR",
                        "data": {
                            "data": {
                                "message": output_verify['err_msg'],
                                "code": 0,
                            }
                        }
                    }
                    return web.Response(status=200, text=json.dumps(err_info))

                json_data['postData'].pop('output')
                form_data = aiohttp.FormData()
                form_data.add_field('json_data', json.dumps(json_data))
                if 'zhutus' in json_data['postData']:
                    for item in json_data['postData']['zhutus']:
                        with open('./input/' + item, 'rb') as f:
                            file_content = f.read()
                        # 文件写入到变量
                        form_data.add_field('zhutus[]', file_content, filename=os.path.basename(item),
                                            content_type='application/octet-stream')
            except Exception as e:
                return web.Response(status=200, text=e)

            async with session.post(upload_url, data=form_data) as response:

                try:
                    response_result = await response.text()
                    print('=================================================')

                    print(response_result)
                    print(response_result)
                    print(response_result)
                    print(response_result)
                    print(response_result)
                    print('=================================================')
                    result = json.loads(response_result)

                    if 'data' in result and isinstance(result['data'], dict):
                        print(result['data'])
                        if 'data' in result['data'] and isinstance(result['data']['data'], dict):
                            result_data = result['data']['data']
                            # 工作流写入
                            if techsid != '' and techsid != 'init' and result_data['code'] == 1:
                                openid = get_openid()
                                await update_worker_flow(json_data['postData']['uniqueid'], output, openid)

                        return web.Response(status=response.status, text=response_result)
                    else:

                        return web.Response(status=response.status, text=await response.text())
                except json.JSONDecodeError as e:
                    return web.Response(status=response.status, text=await response.text())
        else:

            async with session.post(upload_url, json=json_data) as resp:

                # 检查响应的HTTP状态码和内容类型
                if resp.status == 200 and resp.headers.get('Content-Type') == 'application/json':
                    try:
                        other_api_data = await resp.json()
                        result = web.json_response(other_api_data)
                        return result
                    except aiohttp.ContentTypeError:
                        # 如果响应的内容不是JSON格式，处理错误或进行回退操作
                        error_text = await resp.text()
                        return web.Response(text=error_text, status=400)
                if resp.status == 200 and resp.headers.get('Content-Type') == 'text/html; charset=utf-8':

                    try:
                        result = await resp.text()
                        result = json.loads(result)
                        result_data = result['data']

                        if isinstance(result_data, dict) and json_data[
                            'r'] == 'comfyui.apiv2.code' and 'data' in result_data and 'techsid' in result_data['data'][
                            'data']:
                            if len(result_data['data']['data']['techsid']) > len('12345'):
                                set_token(result_data['data']['data']['techsid'])
                                set_openid(result_data['data']['data']['openid'])
                            pass
                        return web.json_response(result)
                    except json.JSONDecodeError as e:
                        return web.Response(status=resp.status, text=await resp.text())
                else:
                    # 如果状态码不是200或内容类型不是application/json，返回错误信息
                    return web.Response(status=resp.status, text=await resp.text())


@server.PromptServer.instance.routes.post("/manager/do_wss")
async def do_wss(request):
    pass


class ComfyMon:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "app_title": ("STRING", {
                    "multiline": False,
                    "default": "这是默认作品标题，请在comfyui中修改",
                    "placeholder": ""
                }),
                "app_desc": ("STRING", {
                    "multiline": False,
                    "default": "这是默认功能介绍，请在comfyui中修改",
                    "placeholder": ""
                }),
                "app_fee": ("INT", {
                    "default": 18,
                    "min": 0,  # 最小值
                    "max": 999999,  # 最大值
                    "step": 1,  # 滑块的步长
                    "display": "number"  # 仅限外观：作为“数字”或“滑块”显示
                }),
                "free_times": ("INT", {
                    "default": 0,
                    "min": 0,  # 最小值
                    "max": 999999,  # 最大值
                    "step": 1,  # 滑块的步长
                    "display": "number"  # 仅限外观：作为“数字”或“滑块”显示
                }),
            },
            "optional": {
                "app_img1(optional)": ("IMAGE",),
                "app_img2(optional)": ("IMAGE",),
                "app_img3(optional)": ("IMAGE",),
                "custom_img1(optional)": ("IMAGE",),
                "custom_img2(optional)": ("IMAGE",),
                "custom_img3(optional)": ("IMAGE",),
                "custom_video1(optional)": ("IMAGE",),
                "custom_video2(optional)": ("IMAGE",),
                "custom_video3(optional)": ("IMAGE",),
                "custom_text1(optional)": ("STRING", {
                    "multiline": False,
                    "forceInput": True,
                    "dynamicPrompts": False
                }),
                "custom_text2(optional)": ("STRING", {
                    "multiline": False,
                    "forceInput": True,
                    "dynamicPrompts": False
                }),
                "custom_text3(optional)": ("STRING", {
                    "multiline": False,
                    "forceInput": True,
                    "dynamicPrompts": False
                }),
                "custom_img1_desc": ("STRING", {
                    "multiline": False,
                    "default": "请上传图片"
                }),
                "custom_img2_desc": ("STRING", {
                    "multiline": False,
                    "default": "请上传图片"
                }),
                "custom_img3_desc": ("STRING", {
                    "multiline": False,
                    "default": "请上传图片"
                }),
                "custom_video1_desc": ("STRING", {
                    "multiline": False,
                    "default": "请上传视频"
                }),
                "custom_video2_desc": ("STRING", {
                    "multiline": False,
                    "default": "请上传视频"
                }),
                "custom_video3_desc": ("STRING", {
                    "multiline": False,
                    "default": "请上传视频"
                }),
                "custom_text1_desc": ("STRING", {
                    "multiline": False,
                    "default": "请输入文本"
                }),
                "custom_text2_desc": ("STRING", {
                    "multiline": False,
                    "default": "请输入文本"
                }),
                "custom_text3_desc": ("STRING", {
                    "multiline": False,
                    "default": "请输入文本"
                }),
            },
            "hidden": {
                "custom_text333333": ("STRING", {
                    "multiline": False,
                    "default": "输入文本"
                }),
            }
        }

    RETURN_TYPES = ()

    CATEGORY = "ComfyMon"


# 文本输入
class ComfyMon_textInput:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "text": ("STRING", {"default": "", "multiline": True, "placeholder": "文本输入"}), }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "main"

    CATEGORY = "ComfyMon"

    @staticmethod
    def main(text):
        return (text,)


WEB_DIRECTORY = "./web"

NODE_CLASS_MAPPINGS = {
    "ComfyMon": ComfyMon,
    "ComfyMon_textInput": ComfyMon_textInput,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyMon": "ComfyMon",
    "ComfyMon_textInput": "textInput"
}
