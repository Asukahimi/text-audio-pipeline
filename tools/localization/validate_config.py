# -*- coding: utf-8 -*-

import json
import os
import sys

from proto_util import CPPTYPE_STRING
from proto_util import get_cpp_type
from proto_util import find_message_types
 
protocol_path = os.path.abspath(os.path.join(os.getcwd(), "..")) + "\\Protocol"
# protocol_path = "E:\\Project\\Designer\\Protocol"
os.system(protocol_path + "\\GenProtoPY.bat")
sys.path.append(protocol_path + "\\resproto")

file_path = "translate_config.json"
translate_config = {}

def validate_field_type(proto_name, field, msg_type):
    if msg_type != CPPTYPE_STRING:
        error_str = "[Error] 非字符串表头, {}.{} ".format(proto_name, field)
        print(error_str)
        return False

    return True

def validate_config_field_type():
    if not translate_config:
        return True

    ret = True
    
    for proto_name, config in translate_config.items():
        for v in config:
            field_name_list = v.split(".")
            n = len(field_name_list)
            field_name_1 = field_name_list[0]
            if n == 1:
                msg_type = get_cpp_type(proto_name, field_name_1)
                ret = ret and validate_field_type(proto_name, field_name_1, msg_type)

            elif n == 2:
                message_types = find_message_types(proto_name, field_name_1)
                if not message_types:
                    error_str = "[Error] 找不到表头, {}.{} ".format(proto_name, field_name_1)
                    print(error_str)
                    ret = False
                    continue

                fields_by_name = message_types.fields_by_name
                if not fields_by_name:
                    continue

                field_name_2 = field_name_list[1]
                field = fields_by_name.get(field_name_2)
                if not field:
                    error_str = "[Error] 找不到表头, {}.{} ".format(proto_name, field_name_2)
                    print(error_str)
                    ret = False
                    continue

                ret = ret and validate_field_type(proto_name, field_name_2, field.cpp_type)

    return ret 

print("\n")
print("##################################################################################################")
print("## 开始检验")

# 1）配置文件json格式
try:
    file = open(file_path, "r" , encoding='utf-8')
    config = file.read()
    file.close()

    # 将字符串转换为JSON对象
    content = json.loads(config)
    if content:
        translate_config = content["Config"]

except ValueError as e:
    print("Invalid JSON format:", str(e))
    print(u"校验失败")
    exit(1)

# 2）配置的字段类型
if not validate_config_field_type():
    print(u"校验失败")
    exit(1)

print(u"校验成功!")