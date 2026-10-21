import os
import time
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

# 键入搜寻路径
directory_path = input('Please enter the directory path:')

print('The process is running...')

start_time = time.time()

def get_all_file_names(directory):
    file_names = []
    for root, _, files in os.walk(directory):
            if 'WwiseAudio\\Media' not in root and 'WwiseAudio\\Localized' not in root:
                for file in files:
                    file_names.append(os.path.join(root, file))
    return sorted(file_names)

file_names = get_all_file_names(directory_path) 

df = pd.DataFrame({
    'ID': range(1, len(file_names) + 1),
    'FilePath':file_names,
    'FileName': [os.path.basename(file) for file in file_names],
    'PackageName': '',
    'VersionName': '',
    'Desc1' :'',
    'Desc2' :'',
    'Desc3' :''
})

# 去掉'FilePath'和'FileName'列中的字符串路径
df['FilePath'] = df['FilePath'].str.replace(r'<CLIENT_CONTENT>\\', '', regex = True)
df['FilePath'] = df['FilePath'].str.replace(r'<CLIENT_CONTENT>\\Assets\\Character\\','',regex = True)
df['FilePath'] = df['FilePath'].str.replace(r'<CLIENT_CONTENT>\\Assets\\','',regex = True)
df['FilePath'] = df['FilePath'].str.replace(r'<CLIENT_CONTENT>\\UI\\Texture\\','',regex = True)
df['FilePath'] = df['FilePath'].str.replace(r'.uasset', '', regex=True)
df['FileName'] = df['FileName'].str.replace(r'.uasset', '', regex=True)
df['FilePath'] = df['FilePath'].str.replace(r'.wem', '', regex=True)
df['FileName'] = df['FileName'].str.replace(r'.wem', '', regex=True)

df.set_index(['ID'], inplace=True)

df.to_excel('OutputAll.xlsx')
wb = load_workbook('OutputAll.xlsx')
ws = wb.active

font = Font(name='微软雅黑', color='FFFFFF')
fill = PatternFill(fgColor='1f1e33', fill_type='solid')
for cell in ws[1]:
        cell.font = font
        cell.fill = fill

ws['B2'].number_format = '@'
for cell in ws['B2:B' + str(len(df) + 1)]:
    cell[0].number_format = '@'

wb.save('OutputAll.xlsx')

end_time = time.time()
elapsed_time = end_time - start_time

print('Excel file created successfully.')
print(f'Elapsed time: {elapsed_time:.2f} seconds')

#运行完毕后，会在存放此python文件的同一文件夹下生成Excel表格。