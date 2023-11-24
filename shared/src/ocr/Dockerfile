FROM debian:trixie-slim

RUN apt-get update && apt-get install -y wget tesseract-ocr python3.11 python-is-python3 python3-pip

RUN mkdir ~/.config
RUN mkdir ~/.config/pip
RUN echo "[global]\nbreak-system-packages = true" >> ~/.config/pip/pip.conf
RUN python -m pip install --upgrade pip

WORKDIR /
RUN wget https://raw.githubusercontent.com/Deathtanium/dockerpractice/master/shared/src/ocr/requirements.txt
RUN pip install -r /requirements.txt

WORKDIR /shared/src/ocr

EXPOSE 5003
