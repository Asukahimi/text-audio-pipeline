# -*- coding: utf-8 -*-
#
# python版本 3.11

import os
import re

from openpyxl import load_workbook

from util import default_sheet_name
from util import txt_text_file_name
from util import se_txt_languages
from util import se_lf
from util import se_lf_upper

from util import SeColName
from util import is_invalid_chinese

txt_source_dir = "SETextTXTSource"
txt_dir = "SETextTXT"

os.makedirs(txt_dir, exist_ok=True)

#已翻译内容 { key:["chs text", "ja text", "ko text"] ... }
translation_dict = {}

#SE文本翻译内容 { ukey: { ["ja text", "ko text"] ... } ... }
se_translation = {}

def generate_func_dir():
    for file in os.listdir(txt_source_dir):
        file_path = os.path.join(txt_source_dir, file)
        if not os.path.isfile(file_path) or not file.endswith(".txt"):
            continue

        print(file_path)
        last_index = file.rfind("_")
        if last_index <= 0:
            continue

        ex_index = file.find(".txt")
        if ex_index <= 0:
            continue

        language = file[last_index + 1:ex_index]

        for v in se_txt_languages: 
            if v == language:
                func_name = file[0:last_index]
                dir = "{}/{}".format(txt_dir, func_name)
                os.makedirs(dir, exist_ok=True)

                output_file = "{}/{}.txt".format(dir, v)
        
                with open(file_path, mode="r", encoding="utf-8") as f:
                    lines = f.readlines()

                    with open(output_file, mode="w", encoding="utf-8") as f:
                        for line in lines:
                            # 注释内容、文件头、空行
                            if not line.startswith("//") and not line.endswith("$header\n") and line.strip() :
                                if line.startswith("@:"):
                                    word = re.search(r'@:\w+', line)
                                    if word:
                                        f.write(word.group() + "\n")
                                        continue

                                f.write(line)

def add_language_text_dict(key, pos, value):
    if not key:
        return
    
    text_list = translation_dict.get(key)
    if not text_list:
        text_list = [None] * len(se_txt_languages) 
        translation_dict.update({key:text_list})

    if pos < len(text_list):
        text_list[pos] = value

def load_translate():
    for sub_dir in os.listdir(txt_dir):
        dir_path = os.path.join(txt_dir, sub_dir)
        if not os.path.isdir(dir_path):
            continue

        for v in se_txt_languages:
            file_path = "{}/{}.txt".format(dir_path, v)
            if not os.path.exists(file_path):
                continue

            # 读取文件内容
            with open(file_path, mode="r", encoding="utf-8") as file:
                content = file.read()

                used_keys = {} 
                column = SeColName[v]

                # 按照以@:开头的行拆分内容（保留拆分字符串）
                content_list = re.findall(r"@:(.*?)(?=\n@:|$)", content, re.DOTALL)

                for text in content_list:
                    idx = text.find("\n")
                    if idx <= 1:
                        continue

                    key = text[0:idx]
                    if key in used_keys:
                        continue
                    
                    value = text[idx + 1:len(text)]
                    if column == SeColName.chs:
                        value = value.replace("\r\n", '').replace("\n", '').replace(se_lf, '').replace(se_lf_upper, '').replace(" ", "")
                    else:
                        value = value.replace(se_lf, '\n').replace(se_lf_upper, '\n')

                    if not value:
                        continue

                    used_keys.update({key:True})
                    add_language_text_dict(key, column, value)

def add_translation(ukey, value):
    if not value:
        return

    translation = se_translation.get(ukey)
    if translation == None:
        translation = []
        se_translation.update({ukey: translation})

    translation.append(value)

def update_se_translation():
    for key, values in translation_dict.items():
        ukey = values[0]
        if not ukey:
            continue

        add_translation(ukey, values)

def generate_text_xlsx():
    workbook = load_workbook(txt_text_file_name)
    sheet = workbook[default_sheet_name]
    if not sheet:
        print("{} do not have {} sheet", txt_text_file_name, default_sheet_name)
        exit(1)

    sheet.delete_rows(2, sheet.max_row)

    row = 2
    keys = sorted(se_translation)

    for ukey in keys:
        if is_invalid_chinese(ukey):
            continue

        items = se_translation.get(ukey)
        if not items:
            continue

        for list_text in items:
            update_sheet_cell(sheet, row, list_text)
            row += 1

    workbook.save(txt_text_file_name)

def update_sheet_cell(sheet, row, list_text):
    col_ukey = 0

    # 翻译列表
    for i in range(len(se_txt_languages)):
        value = None
        if None != list_text:
            value = list_text[i]

        sheet.cell(row=row, column=i+col_ukey+1, value=value)

# 把散文件按功能名进行目录划分
print("1）generate_func_dir ... ")
generate_func_dir()

# 加载翻译
print("2）load_translate ... ")
load_translate()

# 更新se翻译文本
print("3）update_se_translation ... ")
update_se_translation()

# 把文件翻译内容提取到配置表
print("4）generate_text_xlsx ... ")
generate_text_xlsx()

print(u"处理txt文件完成!")