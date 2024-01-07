from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256
import base64

import os
import argparse

def generate_key(password):
    sha = SHA256.new(password.encode())
    return sha.digest()

def decrypt_file(input_file, output_dir, password):
    key = generate_key(password)
    
    with open(input_file, 'rb') as f:
        iv = f.read(AES.block_size)
        ciphertext = f.read()
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
    
    output_file = f'{output_dir}/{os.path.basename(input_file)}'
    
    with open(output_file, 'wb') as f:
        f.write(decrypted)

def main():
    parser = argparse.ArgumentParser(description='文件解密脚本设置项')
    parser.add_argument('-i', '--input-file', help='需要解密的文件的路径', required=True)
    parser.add_argument('-p', '--password', help='解密所需密码', required=True)
    
    args = parser.parse_args()
    
    output_dir = os.path.join(os.path.dirname(args.input_file), 'decrypt_output')
    os.makedirs(output_dir, exist_ok=True)

    decrypt_file(args.input_file, output_dir, args.password)

if __name__ == '__main__':
    main()