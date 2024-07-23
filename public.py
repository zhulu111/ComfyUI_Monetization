"""

"""
import ast
import hashlib
import os

import json
import sys
import uuid
from io import StringIO
import re
from comfy.cli_args import parser

args = parser.parse_args()
if args and args.listen:
    pass
else:
    args = parser.parse_args([])


def get_address():
    return args.listen if args.listen != '0.0.0.0' else '127.0.0.1'


def get_port():
    return args.port



VERSION = '2.0.0'

def write_key_value(key, value, string_io=None):
    """
    向StringIO中写入键值对。

    :param key: 键
    :param value: 值
    :param string_io: 已存在的StringIO对象，如果为None则创建新对象
    :return: 更新后的StringIO对象
    """
    if string_io is None:
        # 如果没有提供StringIO对象，创建一个新的
        string_io = StringIO()
        # 直接写入键值对
        json.dump({key: value}, string_io)
    else:
        # 如果提供了StringIO对象，先读取现有数据
        string_io.seek(0)  # 重置读取位置
        data = json.load(string_io)

        # 更新字典中的键值对
        data[key] = value

        # 清空StringIO对象，准备写入更新后的数据
        string_io.seek(0)
        string_io.truncate()

        # 写入更新后的字典
        json.dump(data, string_io)

    return string_io


def get_value_by_key(key, string_io):
    """
    从StringIO中根据键获取值。

    :param key: 键
    :param string_io: 包含数据的StringIO对象
    :return: 键对应的值，如果键不存在则返回None
    """
    string_io.seek(0)  # 重置读取位置
    data = json.load(string_io)
    return data.get(key)


def delete_key(key, string_io):
    """
    从StringIO中删除指定的键值对。

    :param key: 要删除的键
    :param string_io: 包含数据的StringIO对象
    :return: 更新后的StringIO对象
    """
    string_io.seek(0)  # 重置读取位置
    data = json.load(string_io)

    # 删除指定的键值对
    if key in data:
        del data[key]

    # 清空StringIO对象，准备写入更新后的数据
    string_io.seek(0)
    string_io.truncate()

    # 写入更新后的字典
    json.dump(data, string_io)

    return string_io

    # 示例使用
    # 创建StringIO对象
    # my_stringio = StringIO()
    #
    # # 写入键值对
    # my_stringio = write_key_value('name', 'Alice', my_stringio)
    # my_stringio = write_key_value('age', 30, my_stringio)
    #
    # # 根据键获取值
    # print(get_value_by_key('name', my_stringio))  # 应输出: Alice
    # print(get_value_by_key('age', my_stringio))   # 应输出: 30
    #
    # # 删除键值对
    # my_stringio = delete_key('age', my_stringio)
    #
    # # 再次尝试获取已删除的键值对
    # print(get_value_by_key('age', my_stringio))   # 应输出: None


# 读取文件的内容
def read_json_from_file(name, path='json/', type_1='json'):
    base_url = './custom_nodes/ComfyUI_Monetization/config/' + path
    if not os.path.exists(base_url + name):
        return None

    with open(base_url + name, 'r') as f:
        data = f.read()
        if data == '':
            return None
        if type_1 == 'json':
            try:
                data = json.loads(data)
                return data
            except ValueError as e:
                return None
        if type_1 == 'str':
            return data


def write_json_to_file(data, name, path='json/', type_1='str'):
    """
    将数据以字符串形式写入文件
    """

    base_url = './custom_nodes/ComfyUI_Monetization/config/' + path
    # 判断目录是否存在,不存在则创建 /config/json/
    if not os.path.exists(base_url):
        os.makedirs(base_url)
    if type_1 == 'str':

        # 将数据转换为字符串
        str_data = str(data)
        # 写入文件
        with open(base_url + name, 'w') as f:
            f.write(str_data)
            print(f"String data written to {base_url + name}")
    elif type_1 == 'json':
        with open(base_url + name, 'w') as f:
            json.dump(data, f, indent=2)
            print(f"String data written to {base_url + name}")
#
# def write_json_to_file(data, name, path='json/'):
#     """
#     将数据写入JSON文件
#     """
#
#     base_url = './custom_nodes/ComfyUI_Monetization/config/' + path
#     # 判断目录是否存在,不存在则创建 /config/json/
#     if not os.path.exists(base_url):
#         os.makedirs(base_url)
#     with open(base_url + name, 'w') as f:
#         json.dump(data, f, indent=4)
#         print(f"JSON data written to {name}")


# 凭借得到完整的output
def get_output(uniqueid, path='json/'):
    output = read_json_from_file(uniqueid, path,'json')
    if output is not None:
        # 循环便利  output
        return output
    return None


def get_token():
    # write_json_to_file(result['techsid'], 'techsid'+get_port_from_cmdline()+'.txt','hash/')
    techsid = read_json_from_file('techsid' + str(get_port_from_cmdline()) + '.txt', 'hash/','str')


    if techsid is not None:
        return techsid
    else:
        return 'init'
    pass


def set_token(token):
    write_json_to_file(token, 'techsid' + str(get_port_from_cmdline()) + '.txt', 'hash/')



def set_openid(token):
    write_json_to_file(token, 'openid' + str(get_port_from_cmdline()) + '.txt', 'hash/')

def get_openid():
    openid = read_json_from_file('openid' + str(get_port_from_cmdline()) + '.txt', 'hash/','str')

    if openid is not None:
        return openid
    else:
        return 'init'
    pass

def get_port_from_cmdline():
    for i, arg in enumerate(sys.argv):
        if arg == '--port' and i + 1 < len(sys.argv):
            try:
                return int(sys.argv[i + 1])
            except ValueError:
                pass

        match = re.search(r'--port[=\s]*(\d+)', arg)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass

    # 如果命令行参数中未找到端口号，则返回默认端口号
    return 8188


def get_version():
    return VERSION


def get_mac_address():
    mac = uuid.getnode()
    return ':'.join(('%012X' % mac)[i:i + 2] for i in range(0, 12, 2))


def generate_unique_client_id(port):
    # 根据 MAC 地址和端口号生成唯一的子域名
    unique_key = f"{get_mac_address()}:{port}"
    hash_object = hashlib.sha256(unique_key.encode())
    subdomain = hash_object.hexdigest()[:12]
    return subdomain

