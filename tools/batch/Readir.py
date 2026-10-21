import os
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

# 键入搜寻路径
directory_path = input('Please enter the directory path:')

print('The process is running...')

# 获取文件夹下所有它的子文件夹名
def get_all_subdirectories(directory):
    subdirectories = []
    for root, dirs, _ in os.walk(directory):
        for dir in dirs:
            subdirectories.append(os.path.join(root, dir))
    return sorted(subdirectories)

subdirectories = get_all_subdirectories(directory_path)

# 创建一个DataFrame，包含所需的列
df = pd.DataFrame({
    'ID': range(1, len(subdirectories) + 1),
    'SubdirectoryPath': subdirectories,
    'SubdirectoryName': [os.path.basename(subdir) for subdir in subdirectories],
    'PackageName': '',
    'VersionName': '',
    'Desc1': '',
    'Desc2': '',
    'Desc3': ''
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

wb.save('OutputAll.xlsx')

print('Excel file created successfully.')

# 运行完毕后，会在存放此python文件的同一文件夹下生成Excel表格。