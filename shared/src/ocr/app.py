import os
import socket
import pytesseract as pyt
import cv2
import numpy as np
import sys
import deskew
from PIL import Image
import logging as log
from shared.misc.utils import ThreadedServer

sys.path.append('../../misc')
from utils import *

def correct_image_rotation(img):
    #img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    angle = deskew.determine_skew(thresh)
    pil_img = Image.fromarray(thresh)
    pil_img = pil_img.rotate(angle, expand=True)
    return np.array(pil_img)

def ocr(img):
    return pyt.pytesseract.image_to_string(img, lang='eng+ron', config='--psm 6')

def handle(data):
    log.info("ocr - processing file: {}".format(data['filename']))
    try:
        img = np.frombuffer(data['bytes'].encode('latin-1'), dtype=np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        img = correct_image_rotation(img)
        text = ocr(img)
        log.info("ocr - writing text to file")
        with open(os.path.join('/shared/io/step3', data['filename']+'.txt'), 'w') as f:
            f.write(text)
        log.info("ocr - sending response to driver")
        return {'status':'ok', 'text':text}
    except Exception as e:
        log.error("ocr - error processing file; check ocr logs")
        return {'status':'error', 'error':str(e)}

log.info("Starting OCR")
sockserver = ThreadedServer('ocr', 5003, handle, "/shared/logs/ocr.log")
sockserver.start(handle)



