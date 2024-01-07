import os
from zipfile import ZipFile
import sys

import argparse

parser = argparse.ArgumentParser(description='分块压缩脚本设置项')

parser.add_argument('-d', '--source-dir', required=True, help='需要添加到压缩包的资源目录')
parser.add_argument('-n', '--zip-name', help='压缩包名称 (默认为路径名)')
parser.add_argument('-c', '--chunk-size', type=int, default=1, help='压缩包阈值')
parser.add_argument('-u', '--unit', choices=['GB', 'MB', 'KB', 'B'], default='GB', help='阈值单位')
parser.add_argument('-o', '--output-path', help='压缩包输出目录 (默认为资源目录的上级目录)')

args = parser.parse_args()

source_dir = args.source_dir
zip_name = args.zip_name or os.path.basename(source_dir)
chunk_size = args.chunk_size
unit = args.unit.upper()
parent_dir = args.output_path or os.path.dirname(source_dir)

def convert_size_to_bytes(size, unit):
    units = {'B': 1, 'KB': 1024, 'MB': 1024 ** 2, 'GB': 1024 ** 3}
    return size * units[unit]

def zip_files_by_size(source_dir, chunk_size=1, unit='MB'):
    chunk_size_bytes = convert_size_to_bytes(chunk_size, unit)
    current_chunk = 1
    current_chunk_size = 0
    
    zipf = None

    for folder, _, files in os.walk(source_dir):
        for file in files:
            file_path = os.path.join(folder, file)
            file_size = os.path.getsize(file_path)
            
            if current_chunk_size + file_size > chunk_size_bytes:
                if zipf is not None:
                    zipf.close()
                current_chunk += 1
                current_chunk_size = 0
                zipf = None

            if zipf is None:
                zipf = ZipFile(os.path.join(parent_dir, f'{zip_name}_{current_chunk}.zip'), 'w')

            relative_path = os.path.relpath(file_path, source_dir)
            arcname = os.path.basename(source_dir)
            zipf.write(file_path, arcname=os.path.join(arcname, relative_path))
            current_chunk_size += file_size

    if zipf is not None:
        zipf.close()

zip_files_by_size(source_dir, chunk_size, unit)