import os
import re
import sys

import argparse

parser = argparse.ArgumentParser(description='文件重命名脚本设置项')

parser.add_argument('-d', '--directory-path', default='.', help='目录路径')
parser.add_argument('-n', '--name-startswith', default='file', help='文件前缀')
parser.add_argument('-s', '--start_num', type=int, default=1, help='序号起始值')

args = parser.parse_args()

directory_path = args.directory_path
name_startswith = args.name_startswith
start_num = args.start_num

def rename_files(directory):
    file_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f != os.path.basename(__file__)]
    
    for index, file_name in enumerate(file_files, start=start_num):
        new_name = f'{name_startswith}_{index}.{file_name.split(".")[-1]}'
        
        while os.path.exists(os.path.join(directory, new_name)):
            index += 1
            new_name = f'{name_startswith}_{index}.{file_name.split(".")[-1]}'
        
        old_path = os.path.join(directory, file_name)
        new_path = os.path.join(directory, new_name)
        
        os.rename(old_path, new_path)
        print(f'重命名: {file_name} -> {new_name}')

rename_files(directory_path)