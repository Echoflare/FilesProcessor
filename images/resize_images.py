import os
from PIL import Image,PngImagePlugin
import hashlib
import sys
import numpy as np
import concurrent.futures

import argparse

def process_image(filename, output_filename, scale, resample_method, source_dir):
    global processed_count
    processed_count += 1
    print(f'{processed_count}/{file_count}')
    try:
        image = Image.open(os.path.join(source_dir,filename))
        format = PngImagePlugin.PngImageFile.format
        w = int(image.width * scale)  
        h = int(image.height * scale)
        resized_image = image.resize((w, h), resample=resample_method)
        resized_image.save(output_filename,format=format) 
        image.close()
        resized_image.close()
        os.rename(os.path.join(source_dir,filename), f'{processed_dir}/{filename}')
    except Exception as e:
        print(str(e))
        print(f"缩放 {filename} 文件时出错")

def main():
    parser = argparse.ArgumentParser(description='缩放图片脚本设置项')

    parser.add_argument('-t', '--threads', type=int, help='缩放使用的线程数')
    parser.add_argument('-d', '--source-dir', default='.', help='缩放的目标文件夹路径')
    parser.add_argument('-s', '--scale', type=float, help='缩放的比例')
    parser.add_argument('-r', '--resample', type=str, default='BICUBIC', choices=['NEAREST', 'BOX', 'BILINEAR', 'HAMMING', 'BICUBIC', 'LANCZOS'], help='缩放的采样器')
    parser.add_argument('-y', '--yes', action='store_true', help='自动同意缩放全部文件')

    args = parser.parse_args()

    threads = args.threads
    source_dir = args.source_dir
    scale = args.scale
    resample_method = getattr(Image.Resampling, args.resample)

    if not scale:
        scale = input("请输入缩放比例：")
    
    if scale <= 0 or scale == 1:
        print(f'该缩放比例无意义: {scale}')
        exit()

    if not args.yes:
        while True:
            choice = input("是否缩放全部文件？(y/n)：")
            if choice.lower() == 'y':
                break
            elif choice.lower() == 'n':
                return
    
    global output_dir, processed_dir
    
    output_dir = f"{source_dir}/processed_output"
    processed_dir = f"{source_dir}/procd_unscale_images"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    skipped_files = []  # 存储已跳过的文件名
    
    global file_count, processed_count
    file_count = sum(1 for file in os.listdir(source_dir) if file.endswith(('.jpg', '.jpeg', '.png', '.webp')))
    processed_count = 0
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=threads)
    futures = []
    for filename in os.listdir(source_dir):
        if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.webp') or filename.endswith('.jpeg'): 
            output_filename = os.path.join(output_dir, filename)
            if os.path.exists(output_filename):
                skipped_files.append(filename)
                print(f"已跳过 {filename} 文件")
                processed_count += 1
                print(f'{processed_count}/{file_count}')
                continue
            futures.append(executor.submit(process_image, filename, output_filename, scale, resample_method, source_dir))
    concurrent.futures.wait(futures)
                    
    if skipped_files:
        print("已跳过以下文件：")
        for filename in skipped_files:
            print(filename)

if __name__ == "__main__":
    main()