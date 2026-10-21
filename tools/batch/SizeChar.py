import os

def get_file_sizes(directory):
    file_sizes = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            file_sizes[file] = file_size
    return file_sizes

if __name__ == "__main__":
    directory = input("输入想要查询的文件的路径： ")
    file_sizes = get_file_sizes(directory)

    print("\nFile Sizes:")
    for file, size in file_sizes.items():
        print(f"{file}: {size} bytes")