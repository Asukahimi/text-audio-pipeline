import re

from enum import IntEnum

 # None 为复数列占位
se_languages = ["JA", "KO", "EN", None, "DE", None, "FR", None]
se_txt_languages = ["chs", "ja", "ko", "en", "en_", "de", "de_", "fr", "fr_"]
se_excel_languages = ["ja", "ko", "en", "en_", "de", "de_", "fr", "fr_"]

# 默认sheet名
default_sheet_name = "Sheet1"

# txt文本文件名
txt_text_file_name = "SEText_output/se_text_00_txt.xlsx"

# csv 文本文件名
csv_text_file_name = "SEText_output/se_text_00_csv.xlsx"

# se_text_ukey文件名
se_text_file_name = "SEText_output/se_text_ukey.xlsx"
exc_file_name = "SEText_output/exception.xlsx"

# SE换行符标识
se_lf = "<br>" 
se_lf_upper = "<BR>" 

class SeColName(IntEnum):
    chs     = 0
    ja      = 1
    ko      = 2
    en      = 3
    en_     = 4
    de      = 5
    de_     = 6
    fr      = 7
    fr_     = 8

def is_invalid_chinese(s):
    if not isinstance(s, str):
        return True 

    return not bool(re.search(r'[\u4e00-\u9fa5]', s))