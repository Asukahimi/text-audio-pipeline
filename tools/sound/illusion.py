import os
#获取文件夹路径下的所有txt文件内容和文件名
def get_text_list(file_path):
    files = os.listdir(file_path)
    text_list = []
    for file in files:
        with open(os.path.join(file_path,file),"r",encoding="utf-8") as f:
            text_list.append(f.read())
            return text_list,files