# pull official base image
FROM ubuntu:20.04

RUN rm /bin/sh && ln -s /bin/bash /bin/sh
# set work directory
RUN mkdir  /usr/src/app
WORKDIR  /usr/src/app

# if you forked EasyOCR, you can pass in your own GitHub username to use your fork
# i.e. gh_username=myname
ARG gh_username=JaidedAI
ARG service_home="/home/EasyOCR"
ARG DEBIAN_FRONTEND=noninteractive

# set environment variables
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 카카오 ubuntu archive mirror server 추가. 다운로드 속도 향상
RUN sed -i 's@archive.ubuntu.com@mirror.kakao.com@g' /etc/apt/sources.list 

# Configure apt and install packages
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libffi-dev \
    libglib2.0-0 \
    libsm6 \
    libssl-dev \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-dev \
    python3-dev \
    python3-setuptools \
    python3-pip \
    python3-opencv \
    python-is-python3 \
    python3-venv \
    netcat \
    tesseract-ocr \
    tesseract-ocr-kor \
    tesseract-ocr-jpn \
    ghostscript \
    imagemagick \
    python3-psycopg2 \
    poppler-utils \
    unzip \
    wget \
    git \
    gcc \
    make \
    # cleanup
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/li

# Clone EasyOCR repo
RUN mkdir "$service_home" \
    && git clone "https://github.com/$gh_username/EasyOCR.git" "$service_home" \
    && cd "$service_home" \
    && git remote add upstream "https://github.com/JaidedAI/EasyOCR.git" \
    && git pull upstream master
# Create a virtual environment in /opt
RUN python3 -m venv /opt/venv
RUN source /opt/venv/bin/activate

# Build
RUN cd "$service_home" \
    && python setup.py build_ext --inplace -j 4 \
    && python -m pip install -e .

# purge unused
RUN apt-get remove -y --purge make gcc build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/english_g2.zip
RUN wget https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/korean_g2.zip
RUN wget https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/japanese_g2.zip
RUN wget https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/craft_mlt_25k.zip

RUN mkdir ~/.EasyOCR
RUN mkdir ~/.EasyOCR/model
RUN unzip english_g2.zip -d ~/.EasyOCR/model
RUN unzip korean_g2.zip -d ~/.EasyOCR/model
RUN unzip japanese_g2.zip -d ~/.EasyOCR/model
RUN unzip craft_mlt_25k.zip -d ~/.EasyOCR/model

RUN  pip install --upgrade pip --no-cache-dir && \
     pip install --upgrade setuptools --no-cache-dir && \
     pip install loguru --no-cache-dir && \
     pip install cryptography==2.6.1 --no-cache-dir && \
     pip install Pillow --no-cache-dir && \
     pip install opencv-python --no-cache-dir && \
     pip install pytesseract --no-cache-dir && \
     pip install Image --no-cache-dir && \
     pip install pyyaml --no-cache-dir


# install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir  -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# copy project
COPY . .

# python3를 python으로 alias 설정
# RUN alias python='python3'

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
