import pandas as pd
import os
import time
import openpyxl

print('The process is running...')

newexcel_file_name = 'OutputAll.csv'
oldexcel_file_name = 'WwiseAudio.xlsx'

start_time = time.time()

def parse_csv():
    print('[NOTE] parsing CSV data, wait......')
    data = {}
    with open(newexcel_file_name, 'r') as f:
        csv_reader = pd.read_csv(f)
        for index, row in csv_reader.iterrows():
            ID = row['ID']
            FilePath = row['FilePath']
            FileName = row['FileName']
            PackageName = row['PackageName']
            VersionName = row['VersionName']
            Desc1 = row['Desc1']
            Desc2 = row['Desc2']
            Desc3 = row['Desc3']

            file_path = os.path.join(FilePath, FileName)
            data[file_path] = {
                'ID': ID,
                'FilePath': FilePath,
                'FileName': FileName,
                'PackageName': PackageName,
                'VersionName': VersionName,
                'Desc1': Desc1,
                'Desc2': Desc2,
                'Desc3': Desc3
            }

    return data

def update_excel(excel_data):
    print('[NOTE] updating Excel data, wait......')

    wb = openpyxl.load_workbook(oldexcel_file_name)
    ws = wb.active

    for row_ind in range(2, ws.max_row + 1):
        file_path = ws.cell(row=row_ind, column=2).value  # Assuming 'FilePath' is in column 2
        if file_path in excel_data:
            ws.cell(row=row_ind, column=5).value = excel_data[file_path]['VersionName']  # Assuming 'VersionName' is in column 5
            ws.cell(row=row_ind, column=6).value = excel_data[file_path]['Desc1']  # Assuming 'Desc1' is in column 6
            ws.cell(row=row_ind, column=7).value = excel_data[file_path]['Desc2']  # Assuming 'Desc2' is in column 7
            ws.cell(row=row_ind, column=8).value = excel_data[file_path]['Desc3']  # Assuming 'Desc3' is in column 8
        else:
            print(f"[WARNING] CSV data not contains: {file_path}")

    print('[NOTE] saving Excel data, wait......')
    wb.save(oldexcel_file_name)

csv_data = parse_csv()
update_excel(csv_data)

end_time = time.time()
elapsed_time = end_time - start_time

print('Excel file updated successfully.')
print(f'Elapsed time: {elapsed_time:.2f} seconds')