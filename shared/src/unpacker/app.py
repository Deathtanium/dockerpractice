import py7zr
import shutil
import os
import threading
import socket
import json
import logging as log
import cv2
import numpy as np
from pdf2image import convert_from_path

fh = log.FileHandler("/shared/logs/unpacker.log")

shutil.register_unpack_format('7zip', ['.7z'], py7zr.unpack_7zarchive)

lhost = 'driver'
lport = 5001

rhost = 'optimizer'
rport = 5003

tmp_folder = '/shared/io/step2'

supported_archive = ['7z','zip','rar']
supported_image = ['png']

def handle_data(data:bytes):
    log.info('handle_data - processing data') 
    try:
        data = json.loads(data.decode())
        filename, filebytes = data['filename'], data['bytes']
        ext = filename.split('.')[-1]
        if ext == "png":
            #send to optimizer
            log.info('handle_data - sending to optimizer')
            ret = {
                'filename': filename,
                'bytes': filebytes
            }
            ret = json.dumps(ret).encode()
            return ret
        else:
            log.error("Unsupported file type: {}".format(ext))
            return b''
    except Exception as e:
        log.error('handle_data - {}'.format(e))
        return b''
    
def thread_handler(client:socket.socket, addr):
    log.info('thread_handler - new connection from {}'.format(addr))
    while True:
        try:
            data = client.recv(1024)
            if data:
                fwd_data = handle_data(data)
                res = b''
                if fwd_data:
                    res = json.dumps({'status': 'ok'}).encode()
                else:
                    res = json.dumps({'status': 'error'}).encode()
                client.send(res)
                rsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                rsock.connect((rhost, rport))
                rsock.send(fwd_data)
                rsock.close()
            else:
                log.info('thread_handler - connection closed by {}'.format(addr))
                client.close()
                break
        except Exception as e:
            log.error('thread_handler - {}'.format(e))
            client.close()
            break


log.basicConfig(level=log.INFO, handlers=[fh])
log.info('main - starting unpacker')
if not os.path.exists(tmp_folder):
    os.makedirs(tmp_folder)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((lhost, lport))
sock.listen(5)
while True:
    client, addr = sock.accept()
    threading.Thread(target=thread_handler, args=(client, addr)).start()

