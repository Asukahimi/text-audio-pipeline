import openpyxl
import csv
import time
import os

print('The process is running...')

start_time = time.time()

# Define the file names
wwise_audio_file_name = 'WwiseAudio.csv'
output_all_file_name = 'OutputAll.xlsx'

def parse_wwise_audio():
    print('[NOTE] parsing Wwise audio data, wait......')
    data = {}
    with open(wwise_audio_file_name, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)  # Skip header
        for line in csv_reader:
            id_val = line[0]
            file_path = line[1]
            file_name = line[2]
            package_name = line[3]
            version_name = line[4]
            desc1 = line[5]
            desc2 = line[6]
            desc3 = line[7]

            data[(file_path, file_name)] = {
                'id': id_val,
                'package_name': package_name,
                'version_name': version_name,
                'desc1': desc1,
                'desc2': desc2,
                'desc3': desc3
            }

    return data

def update_output_all(wwise_audio_data):
    print('[NOTE] updating OutputAll data, wait......')

    wb = openpyxl.load_workbook(output_all_file_name)
    ws = wb.active

    file_path_ind = -1
    file_name_ind = -1
    package_name_ind = -1
    version_name_ind = -1

    for col_index, col_name_cell in enumerate(ws[1], 1):
        if col_name_cell.value == 'FilePath':
            file_path_ind = col_index
        if col_name_cell.value == 'FileName':
            file_name_ind = col_index
        if col_name_cell.value == 'PackageName':
            package_name_ind = col_index
        if col_name_cell.value == 'VersionName':
            version_name_ind = col_index

    if file_path_ind == -1 or file_name_ind == -1 or package_name_ind == -1 or version_name_ind == -1:
        print("[ERROR] failed to find required columns: FilePath, FileName, PackageName, VersionName.")
        return

    row_num = ws.max_row
    for row_ind in range(2, row_num + 1):
        file_path_val = ws.cell(row_ind, file_path_ind).value
        file_name_val = ws.cell(row_ind, file_name_ind).value
        key = (file_path_val, file_name_val)

        if key in wwise_audio_data:
            ws.cell(row_ind, package_name_ind).value = wwise_audio_data[key]['package_name']
            ws.cell(row_ind, version_name_ind).value = wwise_audio_data[key]['version_name']
        else:
            print("[WARNING] Wwise audio data not contains matching FilePath and FileName for row", row_ind)

    print('[NOTE] saving OutputAll data, wait......')
    wb.save(output_all_file_name)

if __name__ == '__main__':
    wwise_audio_data = parse_wwise_audio()
    update_output_all(wwise_audio_data)

end_time = time.time()
elapsed_time = end_time - start_time

print('Excel file created successfully.')
print(f'Elapsed time: {elapsed_time:.2f} seconds')