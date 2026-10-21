# -*- coding: utf-8 -*-
#
# python版本 3.11

import sys
import os
import json
import codecs
import csv

from openpyxl import load_workbook

from util import default_sheet_name
from util import csv_text_file_name
from util import se_languages
from util import se_excel_languages
from util import se_lf
from util import se_lf_upper

from util import is_invalid_chinese

csv_dir = "SETextCSV"
type_config_file_name = "se_csv_text_type.json"

ukey_col_suf = "CHS"
se_text_none = "NONE"

#SE文本翻译内容 { ukey: [ ["ja text", "ko text"] ... ] ... }
se_translation = {}

def get_text_type_config():
    file = codecs.open(type_config_file_name, "r", encoding="utf8")
    content = file.read()
    file.close()

    config = json.loads(content)
    return config

def add_translation(ukey, value):
    if not value:
        return

    translation = se_translation.get(ukey)
    if translation == None:
        translation = []
        se_translation.update({ukey: translation})

    translation.append(value)

def load_translation():
    files = os.listdir(csv_dir)

    for file_name in files:
        if not file_name.endswith(".csv"):
            continue

        file_path = "{}/{}".format(csv_dir, file_name)
        print(file_path)

        col_name_dict = None 
        base_name, extension = os.path.splitext(file_name)
        pre_col = base_name.upper() 

        # 读取 CSV 文件
        with open(file_path, mode="r", encoding="utf-8") as csvfile:
            csv_reader = csv.reader(csvfile)
            row_idx = 0

            for row in csv_reader:
                row_idx += 1
                if row_idx < 3:
                    continue

                if row_idx == 3: # 列名
                    col_name_dict = {value: index for index, value in enumerate(row)}
                    continue

                if row_idx < 7: # 实际内容从第7行开始
                    continue

                if not col_name_dict: 
                    break

                # 加载列--单复数
                load_single_plural_col(pre_col, col_name_dict, row)

                # 加载列--配置类型
                load_config_type_col(pre_col, col_name_dict, row)


# 加载列--单复数
# 单数：大写表格名_SGL_语言标识（ITEMTEXT_SGL_EN、ITEMTEXT_SGL_DE、ITEMTEXT_SGL_FR）
# 复数：大写表格名_PLR_语言标识（ITEMTEXT_PLR_EN、ITEMTEXT_PLR_DE、ITEMTEXT_PLR_FR）
def load_single_plural_col(pre_col, col_name_dict, row):
    ukey_col = "{}_{}_{}".format(pre_col, "SGL", ukey_col_suf)
    ukey_col_idx = col_name_dict.get(ukey_col)
    if ukey_col_idx == None:
        return

    ukey = row[ukey_col_idx]
    ukey = ukey.replace("\r\n", '').replace("\n", '').replace(se_lf, '').replace(se_lf_upper, '').replace(" ", "")
    if not ukey or is_invalid_chinese(ukey):
        return

    list_text = []
    is_all_empty = True
    
    for i in range(len(se_languages)):
        v = se_languages[i]

        col_name = None

        if not v:
            last_v = se_languages[i - 1]
            if not last_v:
                print("se_languages config error, check the location of the plural placeholder")
                sys.exit(1)

            else:
                col_name = "{}_{}_{}".format(pre_col, "PLR", last_v)
        
        if not col_name:
            col_name = "{}_{}_{}".format(pre_col, "SGL", v)

        col_idx = col_name_dict.get(col_name)
        text = ""

        if col_idx: 
            text = row[col_idx]  
            text = text.replace(se_lf, '\n').replace(se_lf_upper, '\n')

        if not text or text == se_text_none:
            text = ""
        else:
            is_all_empty = False

        list_text.append(text)

    if not is_all_empty:
        add_translation(ukey, list_text)

# 加载列--配置类型
# 单数：大写表格名_TypeName_语言标识（如ITEMTEXT_UINAME_EN、ITEMTEXT_UINAME_JA）
def load_config_type_col(pre_col, col_name_dict, row):
    if not text_type_config:
        return

    for v in text_type_config:
        new_pre_col = "{}_{}_".format(pre_col, v)
        load_type_col(new_pre_col, col_name_dict, row)

def load_type_col(pre_col, col_name_dict, row):
    ukey_col = pre_col + ukey_col_suf
    ukey_col_idx = col_name_dict.get(ukey_col)
    if ukey_col_idx == None:
        return

    ukey = row[ukey_col_idx]
    ukey = ukey.replace("\r\n", '').replace("\n", '').replace(se_lf, '').replace(se_lf_upper, '').replace(" ", "")
    if not ukey or is_invalid_chinese(ukey):
        return

    list_text = []
    is_all_empty = True
    
    for v in se_languages:
        if not v:
            list_text.append(v)
            continue
        
        col_name = pre_col + v
        col_idx = col_name_dict.get(col_name)
        text = ""

        if col_idx: 
            text = row[col_idx]  
            text = text.replace(se_lf, '\n').replace(se_lf_upper, '\n')

        if not text or text == se_text_none:
            text = ""
        else:
            is_all_empty = False

        list_text.append(text)

    if not is_all_empty:
        add_translation(ukey, list_text)

def generate_text_xlsx():
    workbook = load_workbook(csv_text_file_name)
    sheet = workbook[default_sheet_name]
    if not sheet:
        print(("{} do not have {} sheet").format(csv_text_file_name, default_sheet_name))
        exit(1)

    sheet.delete_rows(2, sheet.max_row)

    row = 2
    keys = sorted(se_translation)

    for ukey in keys:
        items = se_translation.get(ukey)
        if not items:
            continue

        for list_text in items:
            update_sheet_cell(sheet, row, ukey, list_text)
            row += 1

    workbook.save(csv_text_file_name)

def update_sheet_cell(sheet, row, ukey, list_text):
    col_ukey = 1

    # ukey
    sheet.cell(row=row, column=col_ukey, value=ukey)

    # 翻译列表
    for i in range(len(se_excel_languages)):
        value = None
        if None != list_text:
            value = list_text[i]

        sheet.cell(row=row, column=i+col_ukey+1, value=value)

# 加载文本类型名配置
# ..\se_csv_text_type.json
print("1) load_text_type_config ...")
text_type_config = get_text_type_config()

# 加载翻译文本
print("2) load_translation ...")
load_translation()

# 把文件翻译内容提取到配置表
print("3) export_excel ...")
generate_text_xlsx()

print(u"处理csv文件完成!")