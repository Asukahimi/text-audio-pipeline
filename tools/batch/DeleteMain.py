import os

def delete_small_files(directory, size_threshold_kb):
    # 将阈值从KB转换为字节
    size_threshold_bytes = size_threshold_kb * 1024

    # 遍历目录中的所有文件
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            # 如果文件大小小于阈值，则删除文件
            if file_size < size_threshold_bytes:
                print(f"Deleting {file_path} ({file_size} bytes)")
                os.remove(file_path)

# 指定目录和大小阈值
directory = "<CSV_WORK>"
size_threshold_kb = 2

# 删除小于2KB的文件
delete_small_files(directory, size_threshold_kb)
print("Delete Successfully")