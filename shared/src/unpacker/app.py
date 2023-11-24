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
import sys

sys.path.append('../../misc')
from utils import *

fh = log.FileHandler("/shared/logs/unpacker.log")

shutil.register_unpack_format('7zip', ['.7z'], py7zr.unpack_7zarchive)

lhost = 'driver'
lport = 5001

self_host = 'unpacker'
self_port = 5002

rhost = 'ocr'
rport = 5003

out_folder = '/shared/io/step2'

supported_archive = ['7z','zip','rar']
supported_image = ['png']

def handle_data(data:bytes):
    log.info('handle_data - processing data') 
    try:
        data = json.loads(data.decode())
        filename = data['filename']
        filebytes:bytes = data['bytes'].encode('latin-1')
        with open(os.path.join(out_folder, filename), 'wb') as f:
            f.write(filebytes)
        ext = filename.split('.')[-1]
        if ext == "png":
            #send to optimizer
            log.info('handle_data - sending to optimizer')
            ret = {
                'filename': filename,
                'bytes': filebytes.decode('latin-1')
            }
            ret = json.dumps(ret).encode()
            return ret
        else:
            log.warn("Unsupported file type: {}".format(ext))
            return b''
    except Exception as e:
        log.error('handle_data - {}'.format(e))
        return b''
    
def thread_handler(client:socket.socket, addr):
    log.info('thread_handler - new connection from {}'.format(addr))
    while True:
        try:
            data = read_till_null(client)
            if data:
                fwd_data = handle_data(data)
                res = b''
                res = json.dumps({'status': 'ok'}).encode() + b'\0'
                client.send(res)
                rsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                rsock.connect((rhost, rport))
                rsock.send(fwd_data + b'\0')
                rsock.close()
            else:
                log.info('thread_handler - connection closed by {}'.format(addr))
                client.close()
                break
        except Exception as e:
            log.error('thread_handler - {}'.format(e))
            client.close()
            break


sockserver = ThreadedServer(self_host, self_port, thread_handler, "/shared/logs/unpacker.log")
sockserver.listen()
