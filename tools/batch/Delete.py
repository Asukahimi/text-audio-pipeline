import os
import glob

# 设置文件夹路径
folder_path = '<CSV_WORK>'

# 查找所有.d.csv文件
files_to_delete = glob.glob(os.path.join(folder_path, '*.d.csv'))

# 遍历并删除文件
for file_path in files_to_delete:
    try:
        os.remove(file_path)
        print(f'已删除文件：{file_path}')
    except OSError as e:
        print(f'无法删除文件：{file_path}，原因：{e}')
