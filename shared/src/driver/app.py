import socket
import logging as log
import os
import json
import time
import watchdog as wd
import sys

from watchdog.observers import Observer

sys.path.append('../../misc')
from utils import *

input_folder = "/shared/io/step1"
#output_folder = "/shared/step2"

fh = log.FileHandler("/shared/logs/driver.log")

log.basicConfig(handlers=[fh], level=log.INFO)
rhost = 'unpacker'
rport = 5002

log.info("Starting driver")

def read_till_null(sock:socket.socket):
    data = b''
    while True:
        d = sock.recv(1024)
        if not d:
            break
        data += d
        if b'\0' in d:
            break
    data = data[:-1]
    return data

def sendfile(path):
    if os.path.isfile(path):
        log.info("sendfile - processing file: {}".format(os.path.basename(path)))
        try:
            with open(path, "rb") as f:
                data = f.read().decode('latin-1')
            log.info("sendfile - sending request to unpacker")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((rhost, rport))
            data = {
                    'filename':os.path.basename(path),
                    'bytes': data
                }
            s.send(json.dumps(data).encode())
            s.send(b'\0')
            r = read_till_null(s)
            s.close()
            r = json.loads(r.decode())
            log.info("sendfile - received response from unpacker")
            if r['status'] != 'ok':
                log.error("sendfile - error processing file; check unpacker logs")
                return
            os.remove(path)
        except Exception as e:
            log.error("sendfile - error processing file: {}".format(e))
            return

found_files = True
while True:
    time.sleep(5)
    if found_files:
        log.info("main - checking for new files")
        found_files = False
    for f in os.listdir(input_folder):
        found_files = True
        sendfile(os.path.join(input_folder, f))