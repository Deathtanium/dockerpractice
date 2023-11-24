FROM python:3.11.6-slim

RUN apt-get update && apt-get install -y libreoffice wget

WORKDIR /
RUN wget https://raw.githubusercontent.com/Deathtanium/dockerpractice/master/shared/src/unpacker/requirements.txt
RUN pip install -r /requirements.txt

WORKDIR /shared/src/unpacker

EXPOSE 5002
