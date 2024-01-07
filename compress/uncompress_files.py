import os
from zipfile import ZipFile
import sys

import argparse

parser = argparse.ArgumentParser(description='分块压缩脚本设置项')

parser.add_argument('-n', '--zip-name', required=True, help='压缩包名称')
parser.add_argument('-o', '--output-dir', default='.', help='压缩包解压路径 (默认为脚本所在目录)')
parser.add_argument('-r', '--remove-zip', default=False, help='解压后是否删除文件')

args = parser.parse_args()

zip_name = args.zip_name
output_dir = args.output_dir
remove_zip = args.remove_zip

def uncompress_files():
    os.makedirs(output_dir, exist_ok=True)
    zip_files = [file for file in os.listdir('.') if zip_name in file and file.endswith('.zip')]
    for zip_file in zip_files:
        with ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        if remove_zip:
            os.remove(zip_file)

uncompress_files()