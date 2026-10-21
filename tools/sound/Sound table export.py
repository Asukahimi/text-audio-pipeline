# -*- coding: UTF-8 -*-

#需求以sci文件为起始点，导出sci\bpx文件中的各类参数。
#Sci文件路径：<REPO>/<BRANCH>/<VERSION>/gra              此路径下的所有sci文件
#Bpx文件路径：<REPO>/<BRANCH>/<VERSION>/sound         此路径下的所有bpx文件，命名都为default.bpx

#从sci中对应多个sound，根据sound在bpx中对应material，最终每一行是一个material即wav，一个sci、sound会对应多行。

#NOTE: 脚本放在<VERSION>路径下！！！！！！！！！！
#该脚本会删除脚本同级目录下所有以'se_sound_'开头的文件


import xml.etree.ElementTree as ET
import openpyxl
from openpyxl.styles import PatternFill
import os
import collections
import copy
import pandas as pd
import xml

#excel文件拆分行数配置
parse_row_count = 10000

# SE资源中bank的数量
bank_num        = 50000

global current_path
log_file_path = "log.txt"

def get_bpxfiles(root_path):
    bpx_files = []
    for root, dirs, files in os.walk(root_path):
        for f in files:
            # 不止default.bpx里面有音频
            # if f == 'default.bpx':
            if os.path.splitext(f)[1] == '.bpx':
                bpx_files.append(os.path.join(root, f))
    return bpx_files

def parse_kbx(kbx_path):
    kbx_data = {}
    try:
        root = ET.parse(kbx_path).getroot()
        kbx_data['bankindex'] = root.get('BankNumber')
    except FileNotFoundError:
        print ("[WARNING] cannot find kbx file " + kbx_path)
    except xml.etree.ElementTree.ParseError:
        print ("[WARNING] faild to parse kbx file " + kbx_path)
    return kbx_data

wav_name_path_map = {}

def parse_bpx():
    bpx_files = get_bpxfiles(os.path.join(current_path, 'sound'))
    bpx_data = []

    def sound_2d_or_3d(category):
        type_list = ["", "2D", "3D", "3D", "2D", "3D", "3D", "3D", "2D", "2D", "3D", "3D", "3D", "2D", "", "", "3D", "3D", "2D"]
        return type_list[int(category)]

    def add_bpx_sound_data(bpx_sound_data, upper_label, bank_index, is_ambiguous):
        if is_ambiguous:
            bpx_sound_data['is_ambiguous'] = False

        if upper_label not in bpx_data[bank_index]:
            bpx_data[bank_index][upper_label] = {}
        bpx_label_data = bpx_data[bank_index][upper_label]
        if bpx_sound_data['Name'] in bpx_label_data and bpx_label_data[bpx_sound_data['Name']] != bpx_sound_data:
            if is_ambiguous:
                bpx_sound_data['is_ambiguous'] = True
            else:
                log_file.write("[WARNING] Same bank, name and upper label but different bpx data, new bpx path: {},\told bpx path: {}\n".format(f, bpx_label_data[bpx_sound_data['Name']]['BPXFilePath']))
        bpx_label_data[bpx_sound_data['Name']] = bpx_sound_data

    # bpx_data下标为bank的编号, 最后一个用于模糊搜索
    for _ in range(bank_num + 1):
        bpx_data.append({})

    for f in bpx_files:
        try:
            root = ET.parse(f).getroot()
            sounds = root.find('Sounds')
            for sound in sounds.findall('Sound'):
                bpx_sound_data = collections.OrderedDict()
                bpx_sound_data['Name'] = sound.find('Name').text
                bpx_sound_data['EventName'] = ""
                bpx_sound_data['Comment1'] = sound.get('Comment')
                bpx_sound_data['Comment2'] = sound.get('Comment2')
                bpx_sound_data['comment3'] = sound.get('Comment3')
                bpx_sound_data['Type'] = sound.get('Type')
                bpx_sound_data['Output'] = sound.get('Output')
                bpx_sound_data['Volume'] = sound.get('Volume')
                bpx_sound_data['Category'] = sound.get('Category')
                bpx_sound_data['2D/3D'] = sound_2d_or_3d(bpx_sound_data['Category'])
                bpx_sound_data['Priority'] = sound.get('Priority')
                bpx_sound_data['Attribute'] = sound.get('Attribute')
                bpx_sound_data['FixVol'] = sound.get('FixVol')
                bpx_sound_data['FixPos'] = sound.get('FixPos')
                bpx_sound_data['FixDirection'] = sound.get('FixDirection')
                bpx_sound_data['FirstFixPos'] = sound.get('FirstFixPos')
                bpx_sound_data['IsMusic'] = sound.get('IsMusic')
                bpx_sound_data['EnableReverb'] = sound.get('EnableReverb')
                bpx_sound_data['BypassReverb'] = sound.get('BypassReverb')
                bpx_sound_data['ReverbNumber'] = sound.get('ReverbNumber')
                bpx_sound_data['CycleRange'] = sound.get('CycleRange')
                bpx_sound_data['CycleInterval'] = sound.get('CycleInterval')
                bpx_sound_data['CycleNumPlaySeqs'] = sound.get('CycleNumPlaySeqs')
                bpx_sound_data['MaxVolumeRange'] = sound.get('MaxVolumeRange')
                bpx_sound_data['MinVolumeRange'] = sound.get('MinVolumeRange')
                bpx_sound_data['VolumeLossRate'] = sound.get('VolumeLossRate')
                bpx_sound_data['IsForce'] = sound.get('IsForce')
                bpx_sound_data['BPXFilePath'] = os.path.relpath(f, current_path)
                bpx_sound_data['Track'] = []

                bpx_file_dir = os.path.dirname(f)             # 到default那一级
                kbx_file_dir = os.path.dirname(bpx_file_dir)  # 到upper_labbel那一级
                upper_label = os.path.split(kbx_file_dir)[1]

                for sequence in sound.findall('Sequence'):
                    bpx_sequence_data = collections.OrderedDict()
                    bpx_sequence_data['SequenceType'] = sequence.get('Type')
                    bpx_sequence_data['RandomGroup'] = sequence.get('RandomGroup')
                    bpx_sequence_data['Random'] = sequence.get('Random')
                    bpx_sequence_data['IsOrderForcePlay'] = sequence.get('IsOrderForcePlay')

                    track_index = 0
                    for SequenceObject in sequence.findall('SequenceObject'):
                        if SequenceObject.get('Type') == 'Track':
                            bpx_track_data = copy.deepcopy(bpx_sequence_data)
                            bpx_track_data['TrackIndex'] = -1  # 先占个坑, 待会给这个字段赋值
                            bpx_track_data['SequenceObjectType'] = 'Track'
                            bpx_track_data['StartTime'] = SequenceObject.get('StartTime')
                            bpx_track_data['IsLoop'] = SequenceObject.get('IsLoop')
                            bpx_track_data['LinkMaterialNumber'] = SequenceObject.get('LinkMaterialNumber')
                            bpx_track_data['RandomVolumeEnable'] = SequenceObject.get('RandomVolumeEnable')
                            bpx_track_data['RandomVolumeUpper'] = SequenceObject.get('RandomVolumeUpper')
                            bpx_track_data['RandomVolumeLower'] = SequenceObject.get('RandomVolumeLower')
                            bpx_track_data['RandomPitchEnable'] = SequenceObject.get('RandomPitchEnable')
                            bpx_track_data['RandomPitchUpper'] = SequenceObject.get('RandomPitchUpper')
                            bpx_track_data['RandomPitchLower'] = SequenceObject.get('RandomPitchLower')
                            bpx_track_data['RandomPanEnable'] = SequenceObject.get('RandomPanEnable')
                            bpx_track_data['RandomPanUpper'] = SequenceObject.get('RandomPanUpper')
                            bpx_track_data['RandomPanLower'] = SequenceObject.get('RandomPanLower')
                            bpx_track_data['RandomFRPanEnable'] = SequenceObject.get('RandomFRPanEnable')
                            bpx_track_data['RandomFRPanUpper'] = SequenceObject.get('RandomFRPanUpper')
                            bpx_track_data['RandomFRPanLower'] = SequenceObject.get('RandomFRPanLower')
                            bpx_track_data['IsStretched'] = SequenceObject.get('IsStretched')
                            bpx_track_data['StretchedPlayTime'] = SequenceObject.get('StretchedPlayTime')
                            bpx_track_data['EnableFilter'] = SequenceObject.get('EnableFilter')
                            bpx_track_data['FilterType'] = SequenceObject.get('FilterType')
                            bpx_track_data['FilterFrequency'] = SequenceObject.get('FilterFrequency')
                            bpx_track_data['FilterQ'] = SequenceObject.get('FilterQ')
                            bpx_track_data['FilterGain'] = SequenceObject.get('FilterGain')
                            
                            material_number = bpx_track_data['LinkMaterialNumber']
                            for material in root.iter('Material'):
                                if material.get('Number') == material_number:
                                    bpx_track_data['WAV(SE)'] = os.path.join(bpx_file_dir, material.get('Path'))
                                    wav_name = os.path.basename(bpx_track_data['WAV(SE)'])
                                    wav_name = wav_name.split('.')[0]
                                    if wav_name in wav_name_path_map:
                                        wav_name_path_map[wav_name] = 'duplicate_' + wav_name
                                    else:
                                        wav_name_path_map[wav_name] = os.path.relpath(bpx_track_data['WAV(SE)'], current_path)
                                    bpx_track_data['WAV(Project)'] = ''
                                    bpx_track_data['MD5'] = ''
                                    break
                            if 'WAV(SE)' in bpx_track_data:
                                track_index = track_index + 1
                                bpx_track_data['TrackIndex'] = track_index
                                bpx_sound_data['Track'].append(bpx_track_data)

                # TODO - 对于没有track的, 从sci里面提取track数据并填充
                kbx_data = parse_kbx(os.path.join(kbx_file_dir, upper_label + '.kbx'))
                bank_index = int(kbx_data['bankindex'])
                if bank_index >= bank_num:
                    log_file.write("[ERROR] {} bank index {} exceed max bank num {}.\n".format(f, bank_index, bank_num))
                
                # 处理正常检索
                add_bpx_sound_data(bpx_sound_data, upper_label, bank_index, False)

                # 处理模糊检索
                bpx_sound_data = copy.deepcopy(bpx_sound_data)
                add_bpx_sound_data(bpx_sound_data, upper_label, -1, True)

        except FileNotFoundError:
            print ("[WARNING] cannot find bpx file " + f)
        except xml.etree.ElementTree.ParseError:
            print ("[WARNING] faild to parse bpx file " + f)
            #continue
    #print bpx_data
    return bpx_data


def get_scifiles(root_path):
    sci_files = []
    for root, dirs, files in os.walk(root_path):
        for f in files:
            if os.path.splitext(f)[1] == '.sci':
                sci_files.append(os.path.join(root, f))
    return sci_files

def parse_sci():
    sci_data = []
    sci_files = get_scifiles(os.path.join(current_path, 'gra'))
    for f in sci_files:
        row_data = collections.OrderedDict()
        try:
            root = ET.parse(f).getroot()
            sounds = root.find('sounds')
            row_data['SCI'] = f
            row_data['upperlabel'] = sounds.get('upperlabel')
            row_data['bankindex'] = sounds.get('bankindex')
            row_data['busnumber'] = sounds.get('busnumber')
            row_data['sound_list'] = []
            row_data['sound_track'] = {}

            material_track_list = []
            for material in root.find('materials').findall('material'):
                if int(material.get('index')) != len(material_track_list):
                    log_file.write("[Warning] index error, sci: {}, material index: {}.\n".format(f, material.get('index')))
                material_track_list.append(material.find('name').text)

            for sound in sounds.findall('sound'):
                sound_type = sound.get('soundtype')
                if sound_type == 'Empty':
                    continue
                sound_name = sound.get('name')
                sound_dict = {}
                sound_dict['name'] = sound_name
                sound_dict['type'] = sound_type
                sound_dict['tracks'] = []
                sound_track_list = sound_dict['tracks']
                for track in sound.findall('track'):
                    usematerial = track.find('usematerial')
                    if usematerial != None:
                        material_index = usematerial.get('index')
                        sound_track_list.append(material_track_list[int(material_index)])
                    else:
                        log_file.write("[Warning] sci: {}\tsound: {}\t has empty track.\n".format(f, sound_name))
                row_data['sound_list'].append(sound_dict)

        except FileNotFoundError:
            print ("[WARNING] cannot find sci file " + f)
        except xml.etree.ElementTree.ParseError:
            print ("[WARNING] faild to parse sci file " + f)
            continue
        sci_data.append(row_data)
    #print sci_data
    return sci_data

# 根据event name染色
def dye():
    print('[NOTE] coloring excel, wait......')

    last_event_name = ''
    color_fill_list = [
        PatternFill(start_color = 'FCE4D6', fill_type = 'solid'),
        PatternFill(start_color = 'DDEBF7', fill_type = 'solid')
    ]
    color_index = 0

    file_name = 'se_sound.xlsx'
    wb = openpyxl.open(file_name)
    ws = wb.worksheets[0]

    for col_index, col_name_cell in enumerate(ws[1]):
        if col_name_cell.value == 'EventName':
            break

    for row in ws.iter_rows(min_row = 2):
        if last_event_name != row[col_index].value:
            last_event_name = row[col_index].value
            color_index = (color_index + 1) % len(color_fill_list)

        for cell in row:
            cell.fill = color_fill_list[color_index]

    print('[NOTE] saving excel, wait......')
    wb.save(file_name)

sci_except_rows = ['sound_list', 'sound_track']
bpx_except_rows = ['Track', 'is_ambiguous']

def gen_excel_row(sci, bpx, track, ws, row):
    row_data = []
    for _, name in enumerate(sci):
        if name not in sci_except_rows:
            row_data.append(sci[name])

    for _, name in enumerate(bpx):
        if name not in bpx_except_rows:
            row_data.append(bpx[name])

    for _, name in enumerate(track):
        row_data.append(track[name])

    ws.append(row_data)

def gen_excel_omission_row(sci, ws, col_num):
    for sound_dict in sci['sound_list']:
        for track in sound_dict['tracks']:
            row_data = [""] * col_num
            last_index = 0
            for index, name in enumerate(sci):
                if name not in sci_except_rows:
                    row_data[index] = sci[name]
                    last_index = index
            row_data[last_index + 1] = sound_dict['name']
            wav_path = ""
            if track not in wav_name_path_map:
                log_file.write("[Warning] Cannot find wav path {}, sci is {}.\n".format(track, sci['SCI']))
            else:
                wav_path = wav_name_path_map[track]

            if wav_path.startswith == 'duplicate_':
                log_file.write("[Warning] Wav path {} is ambigious, sci is {}.\n".format(track, sci['SCI']))
            row_data[-3] = wav_path
            ws.append(row_data)


def del_excel():
    dir_files = os.listdir(current_path)
    for dir_file in dir_files:
        if dir_file.startswith('se_sound_'):
            file_path = os.path.join(current_path, dir_file)
            if os.path.isfile(file_path):
                os.remove(file_path)

def gen_excel(sci_data, bpx_data):
    if len(sci_data) == 0 or len(bpx_data) == 0:
        print("[ERROR] failed to generate excel because data not complete")
        return

    col_name = []
    for _, name in enumerate(sci_data[0]):
        if name not in sci_except_rows:
            col_name.append(name)

    for _, upper_label in enumerate(bpx_data[1]):
        for _, key in enumerate(bpx_data[1][upper_label]):
            for _, name in enumerate(bpx_data[1][upper_label][key]):
                if name not in bpx_except_rows:
                    col_name.append(name)
            for _, track_param_name in enumerate(bpx_data[1][upper_label][key]['Track'][0]):
                col_name.append(track_param_name)
            break
        break

    def create_sheet(wb, title, col_name_list):
        ws = wb.create_sheet()
        ws.title = title
        ws.append(col_name_list)
        return ws
        
    wb_sound = openpyxl.Workbook(write_only=True)
    ws_sound = create_sheet(wb_sound, "sound", col_name)

    wb_omission = openpyxl.Workbook(write_only=True)
    ws_omission = create_sheet(wb_omission, "omission", col_name)

    row = 0
    file_count = 0

    rel_dir = os.path.join(current_path, 'gra')  # 策划让去掉gra层级

    replacement_dict = {
        ' ': '%20'
    }
    def find_bpx_data(upper_label, bank_index, sound_name):
        # ugit导入的时候空格变成%20
        for old_word, new_word in replacement_dict.items():
            sound_name = sound_name.replace(old_word, new_word)
            upper_label = upper_label.replace(old_word, new_word)
        if upper_label not in bpx_data[bank_index] or sound_name not in bpx_data[bank_index][upper_label]:
            return False
        return bpx_data[bank_index][upper_label][sound_name]

    for sci_row in sci_data:
        relpath = os.path.relpath(sci_row['SCI'], rel_dir)
        sci_row['SCI'] = relpath.replace('.sci', '')

        upper_label = sci_row['upperlabel']
        bank_index = int(sci_row['bankindex'])

        event_name = 'Play_' + os.path.splitext(os.path.basename(sci_row['SCI']))[0]

        for sound_dict in sci_row['sound_list']:
            sound_name = sound_dict['name']
            bpx_sound_data = find_bpx_data(upper_label, bank_index, sound_name)
            if not bpx_sound_data:
                bpx_sound_data = find_bpx_data(upper_label, -1, sound_name)
                if not bpx_sound_data:
                    gen_excel_omission_row(sci_row, ws_omission, len(col_name))
                    log_file.write("[Warning] Cannot find bpx data corresponding with {}, bank is {},\tupper label is {},\t sound name is {}.\n".format(relpath, bank_index, upper_label, sound_name))
                    continue
                if bpx_sound_data['is_ambiguous']:
                    log_file.write("[Warning] Ambiguous bpx data corresponding with {}, bank is {},\tupper label is {},\t sound name is {}.\n".format(relpath, bank_index, upper_label, sound_name))
                    continue

            bpx_sound_data['EventName'] = event_name
            if len(sci_row['sound_list']) > 1:
                bpx_sound_data['EventName'] = event_name + '_' + sound_name

            for track_data in bpx_sound_data['Track']:
                if int(row / parse_row_count) > file_count:

                    # TODO - Remove This!
                    # break

                    xls_path = os.path.join(current_path, 'se_sound_{}.xlsx'.format(file_count))
                    wb_sound.save(xls_path)
                    print('[SUCCESS] generate excel ' + xls_path + ' success!!!')
                    wb_sound = openpyxl.Workbook(write_only = True)
                    ws_sound = create_sheet(wb_sound, "sound", col_name)
                    file_count = file_count + 1

                track_data['WAV(SE)'] = os.path.relpath(track_data['WAV(SE)'], current_path)
                gen_excel_row(sci_row, bpx_sound_data, track_data, ws_sound, row)
                print(str(row))
                row = row + 1 
    print('[NOTE] generate row count: ' + str(row))       
    xls_path = os.path.join(current_path, 'se_sound_{}.xlsx'.format(file_count))
    xls_path_omission = os.path.join(current_path, 'omission_se_sound.xlsx')
    wb_sound.save(xls_path)
    wb_omission.save(xls_path_omission)
    print('[SUCCESS] generate excel ' + xls_path + ' success!!!')
    print('[SUCCESS] generate excel count ' + str(file_count + 1))

def merge_excel():
    print('[NOTE] merge excel, wait......')
    excels = []
    dir_files = os.listdir(current_path)
    for dir_file in dir_files:
        file_path = os.path.join(current_path, dir_file)
        if dir_file.startswith('se_sound_'):
            file_path = os.path.join(current_path, dir_file)
            if os.path.isfile(file_path):
                excels.append(file_path)
    if len(excels) > 0:
        merge_excel_name = 'se_sound.xlsx'
        df = pd.concat([pd.read_excel(excel) for excel in excels])
        df.to_excel(merge_excel_name, index=False)
        for excel in excels:
            os.remove(excel)
        print('[SUCCESS] merge excel '+ os.path.join(current_path, merge_excel_name) + ' success!') 
    else:
        print('[WARNING] no merge excel file')

if __name__ == '__main__':
    current_path = os.getcwd()
    if os.path.isfile(log_file_path):
        os.remove(log_file_path)
    log_file = open(log_file_path, "a")
    sci_data = parse_sci()
    if sci_data != []:
        bpx_data = parse_bpx()
        del_excel()
        gen_excel(sci_data, bpx_data)
        merge_excel()
        dye()
    else:
        print("[WARNING] no sci data")
    log_file.close()
