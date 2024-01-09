import os
import re
import sys

import argparse

parser = argparse.ArgumentParser(description='图片重命名脚本设置项')

parser.add_argument('-d', '--directory-path', default='.', help='目录路径')
parser.add_argument('-n', '--name-startswith', default='image', help='文件前缀')

args = parser.parse_args()

directory_path = args.directory_path
name_startswith = args.name_startswith

def rename_images(directory):
    image_files = [f for f in os.listdir(directory) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    
    for index, file_name in enumerate(image_files, start=1):
        new_name = f'{name_startswith}_{index}.{file_name.split(".")[-1]}'
        
        while os.path.exists(os.path.join(directory, new_name)):
            index += 1
            new_name = f'{name_startswith}_{index}.{file_name.split(".")[-1]}'
        
        old_path = os.path.join(directory, file_name)
        new_path = os.path.join(directory, new_name)
        
        os.rename(old_path, new_path)
        print(f'重命名: {file_name} -> {new_name}')

rename_images(directory_path)