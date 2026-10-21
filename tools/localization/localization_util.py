# -*- coding: utf-8 -*-

import codecs
import json
import re
import os
from localization_cfg import LocalizationCfg
import proto_util

translate_config = {}
designer_path = '''"<WORK_ROOT>\Designer"'''


def load_translate_config(path):
    file_path = "{}/Localization/translate_config.json".format(path)
    file = codecs.open(file_path, "r", encoding="utf8")
    content = file.read()
    file.close()

    config = json.loads(content)
    if None == config:
        return

    global translate_config
    translate_config = config["Config"]

    global designer_path
    designer_path = path


def find_translate_config(protoname):
    global translate_config
    return translate_config.get(protoname)


def find_local_config(local_config, name):
    for v in local_config:
        if v.get("Name") == name:
            return v


def parse_localization_config(local_config, json_config):
    name = json_config[0]
    config = {"Name": name}

    if len(json_config) <= 1:
        local_config.append(config)
    else:
        item = find_local_config(local_config, json_config[0])
        if not item:
            config["Children"] = []
            local_config.append(config)
            parse_localization_config(config.get("Children"), json_config[1:])
        else:
            parse_localization_config(item.get("Children"), json_config[1:])


def get_localization_config(protoname):
    config = find_translate_config(protoname)
    if not config:
        return

    local_config = []
    for v in config:
        l = v.split(".")
        parse_localization_config(local_config, l)

    return local_config


def load_table_cfg(protoname):
    global designer_path
    file_path = "{}/Table/result/{}.json".format(designer_path, protoname)
    if not os.path.exists(file_path):
        return
    file = codecs.open(file_path, "r", encoding="utf8")
    content = file.read()
    file.close()

    data = json.loads(content)
    if None == data:
        return

    return data[1][protoname]


def create_localization_cfg(protoname, property_list):
    if not translate_config:
        return

    config = get_localization_config(protoname)
    if not config:
        return

    data = load_table_cfg(protoname)
    if not data:
        return

    if len(property_list) <= 0:
        return

    keyname = property_list[0].get("Name")
    if not keyname:
        return

    properties = get_localization_properties(protoname, property_list)
    if not properties:
        return

    default_valuel = proto_util.get_default_value(protoname)

    return LocalizationCfg(keyname, data, config, properties, default_valuel)


def get_localization_properties_item(config, property):
    if not config:
        return

    colname = property.get("Name")

    if not next(
            iter(
                filter(
                    lambda v: v == colname or re.sub("\.[\w\W]*", "", v) ==
                    colname, config)), None):
        return

    coltype = property.get("Type")
    cpptype = property.get("CppType")
    label = property.get("Label")
    brepeated = label == proto_util.LABEL_REPEATED
    bmsg = False

    if cpptype == proto_util.CPPTYPE_STRING:
        if brepeated:
            coltype = "INTEGER"
    elif cpptype == proto_util.CPPTYPE_MESSAGE:
        bmsg = True
    else:
        return 

    return {
        "colname": colname,
        "coltype": coltype,
        "brepeated": brepeated,
        "bmsg": bmsg
    }


def get_localization_properties(protoname, property_list):
    properties = {}
    config = find_translate_config(protoname)
    for v in property_list:
        item = get_localization_properties_item(config, v)
        if item:
            properties.update({item.get("colname"): item})
    return properties


# def get_repeated_str_value(text):
#     text = re.sub("^{", "[", text)
#     text = re.sub("}$", "]", text)
#     text = re.sub("<\s*span[\w\W]+?>", "", text)
#     text = re.sub("<\s*img[\w\W]+?>", "", text)
#     text = re.sub("<\s*a[\w\W]+?>", "", text)
#     text = re.sub("\"\"", "\"", text)

#     if len(text) <= 0:
#         return 0
#     return len(json.loads(text, strict=False))

# def get_sub_col_names(config, colname):
#     if not config:
#         return

#     names = []
#     for v in config:
#         l = v.split(".")
#         if len(l) > 1 and l[0] == colname:
#             names.append(l[1])

#     return names

# # 部分表没有json，只能通过字符串匹配处理
# def trim_localization_text(config, colname, text):
#     names = get_sub_col_names(config, colname)
#     if not names or len(names) <= 0:
#         return text

#     text = re.sub("\"\"", "\"", text)

#     for name in names:
#         text = re.sub(pattern_str.format(name), replacement, text)
#         ret = re.findall(pattern_msg.format(name), text)
#         for v in ret:
#             s = re.sub("{}={{".format(name), "[", v)
#             s = re.sub("}$", "]", s)
#             print(text)
#             l = len(json.loads(s, strict=False))
#             text = re.sub(v, "_{}Num={}".format(name, l), text)

#     text = re.sub(",,", ",", text)

#     return text
