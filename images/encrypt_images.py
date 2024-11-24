import os
from PIL import Image,PngImagePlugin
import hashlib
import sys
import numpy as np
import concurrent.futures

import argparse

def get_range(input:str,offset:int,range_len=4):
    offset = offset % len(input)
    return (input*2)[offset:offset+range_len]

def get_sha256(input:str):
    hash_object = hashlib.sha256()
    hash_object.update(input.encode('utf-8'))
    return hash_object.hexdigest()

def shuffle_arr(arr,key):
    sha_key = get_sha256(key)
    arr_len = len(arr)
    for i in range(arr_len):
        to_index = int(get_range(sha_key,i,range_len=8),16) % (arr_len -i)
        arr[i],arr[to_index] = arr[to_index],arr[i]
    return arr

def shuffle_arr_v2(arr,key):
    sha_key = get_sha256(key)
    arr_len = len(arr)
    s_idx = arr_len
    for i in range(arr_len):
        s_idx = arr_len - i - 1
        to_index = int(get_range(sha_key,i,range_len=8),16) % (arr_len -i)
        arr[s_idx],arr[to_index] = arr[to_index],arr[s_idx]
    return arr

def encrypt_image(image:Image.Image, psw):
    width = image.width
    height = image.height
    x_arr = [i for i in range(width)]
    shuffle_arr(x_arr,psw)
    y_arr = [i for i in range(height)]
    shuffle_arr(y_arr,get_sha256(psw))
    pixels = image.load()
    for x in range(width):
        _x = x_arr[x]
        for y in range(height):
            _y = y_arr[y]
            pixels[x, y], pixels[_x,_y] = pixels[_x,_y],pixels[x, y]

def encrypt_image_v2(image:Image.Image, psw):
    width = image.width
    height = image.height
    x_arr = [i for i in range(width)]
    shuffle_arr(x_arr,psw)
    y_arr = [i for i in range(height)]
    shuffle_arr(y_arr,get_sha256(psw))
    pixel_array = np.array(image)

    for y in range(height):
        _y = y_arr[y]
        temp = pixel_array[y].copy()
        pixel_array[y] = pixel_array[_y]
        pixel_array[_y] = temp
    pixel_array = np.transpose(pixel_array, axes=(1, 0, 2))
    for x in range(width):
        _x = x_arr[x]
        temp = pixel_array[x].copy()
        pixel_array[x] = pixel_array[_x]
        pixel_array[_x] = temp
    pixel_array = np.transpose(pixel_array, axes=(1, 0, 2))

    image.paste(Image.fromarray(pixel_array))
    return image

def encrypt_image_v3(image:Image.Image, psw):
    '''
    return: pixel_array
    '''
    width = image.width
    height = image.height
    x_arr = np.arange(width)
    shuffle_arr_v2(x_arr,psw) 
    y_arr = np.arange(height)
    shuffle_arr_v2(y_arr,get_sha256(psw))
    pixel_array = np.array(image)
    
    _pixel_array = pixel_array.copy()
    for x in range(height): 
        pixel_array[x] = _pixel_array[y_arr[x]]
    pixel_array = np.transpose(pixel_array, axes=(1, 0, 2))
    
    _pixel_array = pixel_array.copy()
    for x in range(width): 
        pixel_array[x] = _pixel_array[x_arr[x]]
    pixel_array = np.transpose(pixel_array, axes=(1, 0, 2))

    return pixel_array

def process_image(filename, output_filename, password, source_dir):
    global encrypt_count
    encrypt_count += 1
    print(f'{encrypt_count}/{file_count}')
    try:
        image = Image.open(os.path.join(source_dir,filename))
        image.paste(Image.fromarray(encrypt_image_v3(image, password)))
        format = PngImagePlugin.PngImageFile.format
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text('Encrypt', 'pixel_shuffle_3')
        image.save(output_filename,pnginfo=pnginfo,format=format)
        image.close()
        os.rename(os.path.join(source_dir,filename), f'{processed_dir}/{filename}')
    except Exception as e:
        print(str(e))
        print(f"加密 {filename} 文件时出错")

def main():
    parser = argparse.ArgumentParser(description='加密图片脚本设置项')

    parser.add_argument('-t', '--threads', type=int, help='加密使用的线程数')
    parser.add_argument('-d', '--encrypt-dir', default='.', help='加密的目标文件夹路径')
    parser.add_argument('-p', '--password', help='加密所需密码')
    parser.add_argument('-y', '--yes', action='store_true', help='自动同意加密全部文件')

    args = parser.parse_args()

    threads = args.threads
    encrypt_dir = args.encrypt_dir
    password = args.password

    if not password:
        password = input("请输入密码：")
    
    password = get_sha256(password)
    print(password)

    if not args.yes:
        while True:
            choice = input("是否加密全部文件？(y/n)：")
            if choice.lower() == 'y':
                break
            elif choice.lower() == 'n':
                return
    
    global output_dir, processed_dir
    
    output_dir = f"{encrypt_dir}/encrypt_output"
    processed_dir = f"{encrypt_dir}/procd_decr_images"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    skipped_files = []  # 存储已跳过的文件名
    
    global file_count, encrypt_count
    file_count = sum(1 for file in os.listdir(encrypt_dir) if file.endswith(('.jpg', '.jpeg', '.png', '.webp')))
    encrypt_count = 0
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=threads)
    futures = []
    for filename in os.listdir(encrypt_dir):
        if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.webp') or filename.endswith('.jpeg'): 
            output_filename = os.path.join(output_dir, filename)
            if os.path.exists(output_filename):
                skipped_files.append(filename)
                print(f"已跳过 {filename} 文件")
                encrypt_count += 1
                print(f'{encrypt_count}/{file_count}')
                continue
            futures.append(executor.submit(process_image, filename, output_filename, password, encrypt_dir))
    concurrent.futures.wait(futures)
                    
    if skipped_files:
        print("已跳过以下文件：")
        for filename in skipped_files:
            print(filename)

if __name__ == "__main__":
    main()