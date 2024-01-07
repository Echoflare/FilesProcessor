import os
from zipfile import ZipFile
import sys

import argparse

parser = argparse.ArgumentParser(description='分块压缩脚本设置项')

parser.add_argument('-d', '--source-dir', required=True, help='需要添加到压缩包的资源目录')
parser.add_argument('-n', '--zip-name', help='压缩包名称 (默认为路径名)')
parser.add_argument('-c', '--chunk-size', type=int, default=300, help='压缩包阈值 (文件数)')
parser.add_argument('-o', '--output-path', help='压缩包输出目录 (默认为资源目录的上级目录)')

args = parser.parse_args()

source_dir = args.source_dir
zip_name = args.zip_name or os.path.basename(source_dir)
chunk_size = args.chunk_size
parent_dir = args.output_path or os.path.dirname(source_dir)

def zip_files_by_count(source_dir, chunk_size):
    current_chunk = 1
    files_in_current_chunk = 0
    
    zipf = None

    for folder, _, files in os.walk(source_dir):
        for file in files:
            if files_in_current_chunk == 0 or zipf is None:
                zipf = ZipFile(os.path.join(parent_dir, f'{zip_name}_{current_chunk}.zip'), 'w')

            file_path = os.path.join(folder, file)
            relative_path = os.path.relpath(file_path, source_dir)
            arcname = os.path.basename(source_dir)
            zipf.write(file_path, arcname=os.path.join(arcname, relative_path))
            files_in_current_chunk += 1
            
            if files_in_current_chunk >= chunk_size:
                zipf.close()
                current_chunk += 1
                files_in_current_chunk = 0
                zipf = None

    if zipf is not None:
        zipf.close()

zip_files_by_count(source_dir, chunk_size)
