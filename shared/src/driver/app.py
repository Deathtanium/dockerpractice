import socket
import logging as log
import os
import json

input_folder = "/shared/io/step1"
#output_folder = "/shared/step2"

fh = log.FileHandler("/shared/logs/driver.log")

log.basicConfig(handlers=[fh], level=log.INFO)
rhost = 'unpacker'
rport = 5002

log.info("Starting driver")
while True:
    for filename in os.listdir(input_folder):
        log.info("Processing file: {}".format(filename))
        try:
            with open(os.path.join(input_folder, filename), "rb") as f:
                data = f.read()
            log.info("Sending request to unpacker")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((rhost, rport))
            data = {
                    'filename':filename,
                    'bytes': data
                }
            s.send(json.dumps(data).encode())
            r = s.recv(1024)
            s.close()
            r = json.loads(r.decode())
            log.info("Received response from unpacker")
            if r['status'] != 'ok':
                log.error("Error processing file: {}".format(r.text))
                continue
            os.remove(os.path.join(input_folder, filename))
        except Exception as e:
            log.error("Error processing file: {}".format(e))
            continue
        
