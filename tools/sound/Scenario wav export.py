# -*- coding: UTF-8 -*-

# 需要SoundExportList.txt, 里面是sci名
# 需要脚本文件, SoundExportList.txt, se_sound.xlsx, sound, gra在同一目录下
# 导出的wav文件在sound_export里面, 信息在SoundExportList.xlsx里



import openpyxl
import os
import shutil
from openpyxl.styles import PatternFill



txt_file_name = 'ScenarioExportList.txt'
sound_file_name = 'scenario.xlsx'
export_path = 'sound_export'
export_sound_name = 'ScenarioExportList.xlsx'

def parse_txt():
    sci_set = set()
    with open(txt_file_name, 'r') as f:
        sci_set = {line.strip() for line in f}
    if '' in sci_set:
        sci_set.remove('')
    return sci_set

def parse_xlsx(sci_set):
    print('[NOTE] parsing sound data, wait......')
    wb_read = openpyxl.open(sound_file_name)
    ws_read = wb_read.worksheets[0]

    col_ind_dict = {
        'SCI': -1,
        'WAV(Project)': -1,
        'MD5': -1,
        'WAV(SE)': -1
    }

    for col_index, col_name_cell in enumerate(ws_read[1], 1):
        if col_name_cell.value in col_ind_dict:
            col_ind_dict[col_name_cell.value] = col_index
    
    if -1 in col_ind_dict.values():
        print("[ERROR] failed to find column sci, WAV or MD5.")
        return

    if not os.path.exists(export_path):
        os.mkdir(export_path)

    parsed_sci_set = set()
    row_set = {1}
    row_num = ws_read.max_row

    print('[NOTE] copying wav data, wait......')
    for row_ind in range(2, row_num + 1):
        sci_full_path = ws_read.cell(row_ind, col_ind_dict['SCI']).value
        sci_path = os.path.splitext(os.path.basename(sci_full_path))[0]

        if sci_path in sci_set:
            parsed_sci_set.add(sci_path)
        elif sci_full_path in sci_set:
            parsed_sci_set.add(sci_full_path)
        else:
            continue

        row_set.add(row_ind)

        se_wav_path = ws_read.cell(row_ind, col_ind_dict['WAV(SE)']).value
        fm_wav_name = ws_read.cell(row_ind, col_ind_dict['WAV(Project)']).value
        if not fm_wav_name:
            continue
        fm_wav_name = os.path.relpath(fm_wav_name, 'sound')
        export_wav_name = os.path.join(export_path, fm_wav_name)

        if os.path.exists(export_wav_name):
            continue

        dir_name = os.path.dirname(export_wav_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        try:
            shutil.copyfile(se_wav_path, export_wav_name)
        except FileNotFoundError:
            print('[WARNING] No such file or directory', se_wav_path)

    print('[NOTE] saving sound data, wait......')
    wb_write = openpyxl.Workbook(write_only = True)
    ws_write = wb_write.create_sheet()
    ws_write.title = "sound"

    for row_ind, row in enumerate(ws_read.iter_rows(min_row = 1), 1):
        if row_ind in row_set:
            ws_write.append([cell.value for cell in row])

    ws_sci_miss = wb_write.create_sheet()
    ws_sci_miss.title = "sci_miss"
    for sci in sci_set:
        if sci not in parsed_sci_set:
            print('[WARNING] sci {} not found in xlsx.'.format(sci))
            ws_sci_miss.append([sci])

    wb_write.save(export_sound_name)

# 完全相同的事件做拆分
def divide_into_auto_and_artificial():
    print('[NOTE] dividing excel into auto and artificial, wait......')
    file_name = export_sound_name
    wb = openpyxl.open(file_name)
    ws = wb.worksheets[0]
    ws.append(["end"])

    ws_auto = wb.create_sheet()
    ws_auto.title = "auto"
    ws_auto.append([cell.value for cell in ws[1]])
    ws_artificial = wb.create_sheet()
    ws_artificial.title = "artificial"
    ws_artificial.append([cell.value for cell in ws[1]])

    col_index_dict = {
        "name": -1,
        "Loop": -1,
        "type": -1,
        "PlayTime": -1,
        "CaptionTime":  -1,
        "Volume":  -1,
        "Priority":  -1,
    }
    last_values = {}
    last_event_name = ""
    last_event_row_index = -1

    for col_index, col_name_cell in enumerate(ws[1]):
        if col_name_cell.value in col_index_dict:
            col_index_dict[col_name_cell.value] = col_index

    def add_rows_to_sheet(ws_to_add, start_row_index, end_row_index):
        for row_index in range(start_row_index, end_row_index):
            ws_to_add.append([cell.value for cell in ws[row_index]])



    
    wb.save(file_name)

    print('[NOTE] saving excel, wait......')
    wb.save(file_name)


if __name__ == '__main__':
    sci_set = parse_txt()
    parse_xlsx(sci_set)
    divide_into_auto_and_artificial()
