
FROM ubuntu:18.04

# set environment variables
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update -yqq

RUN apt -yqq install software-properties-common

RUN add-apt-repository ppa:alex-p/tesseract-ocr-devel -y

RUN apt -yqq install build-essential && \
    apt -yqq install libffi-dev && \
    apt -yqq install libssl-dev && \
    apt -yqq install python3-dev && \
    apt -yqq install python3-pip && \
    apt -yqq install mysql-server && \
    apt -yqq install default-libmysqlclient-dev && \
    apt -yqq install tesseract-ocr && \
    apt -yqq install tesseract-ocr-kor && \
    apt -yqq install tesseract-ocr-jpn && \
    apt -yqq install ghostscript && \
    apt -yqq install imagemagick
    # Sudo apt-get install build-essential libssl-dev libffi-dev python3-dev

RUN  pip3 install --upgrade pip --no-cache-dir && \
     pip3 install --upgrade setuptools --no-cache-dir && \
     pip3 install loguru --no-cache-dir && \
     pip3 install cryptography==2.6.1 --no-cache-dir && \
     pip3 install opencv-python --no-cache-dir && \
     pip3 install pytesseract --no-cache-dir && \
     pip3 install easyocr --no-cache-dir && \
     pip3 install Pillow --no-cache-dir && \
     pip3 install Image --no-cache-dir && \
     pip3 install pyyaml --no-cache-dir
     
# install python dependencies
COPY requirements.txt .
RUN  pip3 install --no-cache-dir -r requirements.txt

COPY . .

# gunicorn
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "run:app"]
