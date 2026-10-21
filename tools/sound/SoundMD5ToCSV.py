# -*- coding: UTF-8 -*-
# 将某文件夹下所有wav文件MD5信息提取, 转成excel表格, 命令行参数为文件夹路径

import os
import sys
import hashlib
import csv


# 遍历所有wav文件, 获取信息
def extract_sound_info(sound_dir):
    print('[NOTE] finding wav data, wait......')
    sound_info_list = []
    suffix_list = ['wav', 'aif', 'aiff']

    for dir_path, dir_names, file_names in os.walk(sound_dir):
        for file_name in file_names:
            suffix = file_name.split('.')[-1]
            if suffix not in suffix_list:
                continue

            sound_info = {}
            sound_info["path"] = dir_path
            sound_info["file name"] = file_name
            sound_info["md5"] = ""

            with open(dir_path + '\\' + file_name, "rb") as f:
                sound_data = f.read()
                sound_info["md5"] = hashlib.md5(sound_data).hexdigest()
            
            sound_info_list.append(sound_info)
            if len(sound_info_list) % 50 == 0:
                print(len(sound_info_list))

    return sound_info_list

# 将字典列表以CSV格式存储
def save_csv(sound_info_list, sound_dir):
    header_list = ["path", "file name", "md5"]

    print('[NOTE] saving wav data, wait......')
    with open(sound_dir + "\\SoundMD5.csv", mode = "w", newline = '') as f:
        writer = csv.DictWriter(f, header_list)
        writer.writeheader()
        writer.writerows(sound_info_list)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sound_dir = 'sound'
    else:
        sound_dir = sys.argv[1]
    sound_info_list = extract_sound_info(sound_dir)

    sound_info_list.sort(
        key = lambda sound_info : sound_info["md5"] + sound_info["path"] + sound_info["file name"],
        reverse = True)

    save_csv(sound_info_list, sound_dir)
