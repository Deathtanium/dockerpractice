# Use an official Python runtime as a parent image
FROM python:3.11.6-slim

# Set the working directory to /app
ADD /c/Users/misho/Desktop/dockerpractice/shared /shared
WORKDIR /shared/src/unpacker

# Install any needed packages specified in requirements.txt
RUN pip install -r /shared/src/unpacker/requirements.txt

# Install LibreOffice
RUN apt-get update && apt-get install -y libreoffice

# Make port 80 available to the world outside this container
EXPOSE 5002
