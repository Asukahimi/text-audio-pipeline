import os
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

# 键入搜寻路径
directory_path = input('Please enter the directory path:')

print('The process is running...')

# 获取文件夹下所有文件名与它的子文件夹
def get_all_file_names(directory):
    file_names = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_names.append(os.path.join(root, file))
    return sorted(file_names)

file_names = get_all_file_names(directory_path) 

# 创建一个DataFrame，包含所需的列
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

# 去掉'FilePath'和'FileName'列中的指定前缀和后缀
df['FilePath'] = df['FilePath'].str.replace('<CLIENT_CONTENT>\\', '', regex = True)
df['FilePath'] = df['FilePath'].str.replace('<CLIENT_CONTENT>\Assets\Character\\','',regex = True)
df['FilePath'] = df['FilePath'].str.replace('<CLIENT_CONTENT>\Assets\\','',regex = True)
df['FilePath'] = df['FilePath'].str.replace('<CLIENT_CONTENT>\UI\Texture\\','',regex = True)
df['FileName'] = df['FileName'].str.replace('.uasset', '', regex = True)
df['FileName'] = df['FileName'].str.replace('.wem', '', regex = True)


# 将'序号'列设为索引
df.set_index(['ID'], inplace=True)

# 保存DataFrame到Excel文件
df.to_excel('OutputAll.xlsx')

# 编辑导出的Excel文件，并进行操作
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

print('Excel file created successfully.')

#运行完毕后，会在存放此python文件的同一文件夹下生成Excel表格。