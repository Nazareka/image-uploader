# pull official base image
FROM python:3.9

# set work directory
WORKDIR /image-uploader

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . /image-uploader/
