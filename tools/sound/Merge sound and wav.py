# -*- coding: UTF-8 -*-

# 从wav表提取数据, 与sound表合并
# 需要脚本文件, SoundMD5.csv和se_sound.xlsx三个文件在同一目录下
# wav表命名为SoundMD5.csv, sound表命名为se_sound.xlsx, 结果存到sound表中



import openpyxl
import csv
import os



wav_file_name = 'SoundMD5.csv'
sound_file_name = 'se_sound.xlsx'

def parse_wav():
    print('[NOTE] parsing wav data, wait......')
    data = {}
    with open(wav_file_name, 'r') as f:
        csv_reader = csv.reader(f)
        for line in csv_reader:
            path = line[0]
            name = line[1]
            md5 = line[2]

            file_path = os.path.join(path[path.find('sound'):], name)
            data[file_path] = md5

            if md5 in data and data[md5] <= file_path:
                continue
            data[md5] = file_path

    return data

def parse_sound(wav_data):
    print('[NOTE] parsing sound data, wait......')

    wb = openpyxl.open(sound_file_name)
    ws = wb.worksheets[0]

    se_wav_ind = -1
    fm_wav_ind = -1
    md5_ind = -1

    for col_index, col_name_cell in enumerate(ws[1], 1):
        if col_name_cell.value == 'WAV(Project)':
            fm_wav_ind = col_index
        if col_name_cell.value == 'MD5':
            md5_ind = col_index
        if col_name_cell.value == 'WAV(SE)':
            se_wav_ind = col_index
    
    if fm_wav_ind == -1 or md5_ind == -1 or se_wav_ind == -1:
        print("[ERROR] failed to find column WAV(Project) and MD5.")
        return
    
    row_num = ws.max_row
    for row_ind in range(2, row_num + 1):
        se_wav_path = ws.cell(row_ind, se_wav_ind).value
        if se_wav_path in wav_data:
            md5 = wav_data[se_wav_path]
            ws.cell(row_ind, md5_ind).value = md5
            wav_file_name = wav_data[md5]
            sound_suffix = wav_file_name.split('.')[-1]
            ws.cell(row_ind, fm_wav_ind).value = wav_file_name.replace('.' + sound_suffix, '_' + wav_data[se_wav_path][-4:] + '.' + sound_suffix)
        else:
            print("[WARNING] wav data not contains ", se_wav_path)

    print('[NOTE] saving sound data, wait......')
    wb.save(sound_file_name)



if __name__ == '__main__':
    wav_data = parse_wav()
    parse_sound(wav_data)
