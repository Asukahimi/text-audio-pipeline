sound_table_export = __import__("Sound table export")
import os
import openpyxl
import collections



log_file_path = sound_table_export.log_file_path



def gen_scenario_excel(sci_data):
    if len(sci_data) == 0:
        print("[ERROR] failed to generate excel because data not complete")
        return

    col_name = []
    for _, name in enumerate(sci_data[0]):
        if name not in sound_table_export.sci_except_rows:
            col_name.append(name)
    
    for _, name in enumerate(sci_data[0]['sound_list'][0]):
        if name != 'tracks':
            col_name.append(name)

    col_name = col_name + ['EventName', 'WAV(SE)', 'WAV(Project)', 'MD5']

    def create_sheet(wb, title, col_name_list):
        ws = wb.create_sheet()
        ws.title = title
        ws.append(col_name_list)
        return ws
        
    wb = openpyxl.Workbook(write_only=True)
    ws = create_sheet(wb, "scenario", col_name)

    row = 0

    rel_dir = os.path.join(sound_table_export.current_path, 'gra')  # 策划让去掉gra层级

    for sci_row in sci_data:
        relpath = os.path.relpath(sci_row['SCI'], rel_dir)
        sci_row['SCI'] = relpath.replace('.sci', '')

        upper_label = sci_row['upperlabel']
        bank_index = int(sci_row['bankindex'])

        event_name = 'Play_' + os.path.splitext(os.path.basename(sci_row['SCI']))[0]

        for sound_dict in sci_row['sound_list']:
            sound_name = sound_dict['name']
            # track_data['WAV(SE)'] = os.path.relpath(track_data['WAV(SE)'], current_path)
            if sound_dict['type'] != "Dialog":
                continue

            del sound_dict['tracks']
            sound_dict['Volume'] = int(sound_dict['Volume']) / 100  # 和其他的保持一致

            lang_suffix = sci_row['SCI'].split('_')[-1].replace('chs', 'zh')
            wav_se_path = 'sound\\<VOICE_DIR>\\{}\\{}\\{}.wav'.format(upper_label, lang_suffix, sound_name)

            extra_param_dict = collections.OrderedDict()
            extra_param_dict['EventName'] = event_name
            extra_param_dict['WAV(SE)'] = wav_se_path
            sound_table_export.gen_excel_row(sci_row, sound_dict, extra_param_dict, ws, row)

            if row % 5000 == 0:
                print(str(row))
            row = row + 1

    print('[NOTE] generate row count: ' + str(row))       
    xls_path = os.path.join(sound_table_export.current_path, 'se_sound.xlsx')
    wb.save(xls_path)
    print('[SUCCESS] generate excel ' + xls_path + ' success!!!')



if __name__ == '__main__':
    sound_table_export.current_path = os.getcwd()
    if os.path.isfile(log_file_path):
        os.remove(log_file_path)
    sound_table_export.log_file = open(log_file_path, "a")
    sci_data = sound_table_export.parse_sci({
        "PlayTime": "playtime",
        "CaptionTime": "captiontime",
        "Volume": "volume",
        "Priority": "priority",
        "Loop": "loop"
    })
    if sci_data != []:
        gen_scenario_excel(sci_data)
        sound_table_export.dye()
    else:
        print("[WARNING] no sci data")
    sound_table_export.log_file.close()
