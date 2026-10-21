# -*- coding: utf-8 -*-
#
# python版本 3.11

from openpyxl import load_workbook

from util import se_excel_languages
from util import default_sheet_name
from util import txt_text_file_name
from util import csv_text_file_name
from util import se_text_file_name
from util import exc_file_name
from util import se_txt_languages

#SE文本翻译内容 { ukey: [ ["ja text", "ko text"] ... ] ... }
se_translation = {}

def add_translation(ukey, value):
    if not value:
        return

    translation = se_translation.get(ukey)
    if translation == None:
        translation = []
        se_translation.update({ukey: translation})

    first_value = translation[0] if len(translation) > 0 else None
    if first_value != value:
        translation.append(value)

# 加载翻译文本
def load_translation():
    # 加载txt
    print("load_translation: " + txt_text_file_name)
    load_translation_xlsx(txt_text_file_name)

    # 加载csv
    print("load_translation: " + csv_text_file_name)
    load_translation_xlsx(csv_text_file_name)

def load_translation_xlsx(file_name):
    workbook = load_workbook(file_name)
    sheet = workbook[default_sheet_name]

    ukey_col = 1

    for i in range(1, sheet.max_row):
        row = i + 1

        ukey_cell = sheet.cell(row, ukey_col)

        list_text = []

        for j in range(len(se_txt_languages)):
            if j > 0:
                textcell = sheet.cell(row, j + ukey_col)
                list_text.append(textcell.value)

        add_translation(ukey_cell.value, list_text)

# 导出到Excel
def export_excel():
    workbook = load_workbook(se_text_file_name)
    sheet = workbook[default_sheet_name]
    if not sheet:
        print("{} do not have {} sheet", se_text_file_name, default_sheet_name)
        exit(1)

    exc_workbook = load_workbook(exc_file_name)
    exc_sheet = exc_workbook[default_sheet_name]
    if not exc_sheet:
        print("{} do not have {} sheet", exc_file_name, default_sheet_name)
        exit(1)

    sheet.delete_rows(2, sheet.max_row)
    exc_sheet.delete_rows(2, exc_sheet.max_row)

    row = 2
    exc_row = 2
    keys = sorted(se_translation)

    for ukey in keys:
        items = se_translation.get(ukey)
        if not items:
            continue

        count = len(items)
        if count <= 0:
            continue

        # 第一条数据作为标准翻译
        first_item = items[0]
        if not first_item:
            continue

        update_sheet_cell(sheet, row, ukey, first_item)

        # 异常：一对多的翻译
        if count > 1:
            for list_text in items:
                update_sheet_cell(exc_sheet, exc_row, ukey, list_text)
                exc_row += 1

        row += 1

    workbook.save(se_text_file_name)
    exc_workbook.save(exc_file_name)

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

# 加载翻译文本
print("1) load_translation ...")
load_translation()

# 导出翻译excel
print("2) export_excel ...")
export_excel()

print(u"合并SE文件完成!")
