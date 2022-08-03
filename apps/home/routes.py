# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask_login import login_required
from jinja2 import TemplateNotFound

# -*- coding: utf-8 -*-
from flask import Flask, request, make_response, render_template, url_for, g, send_from_directory, jsonify, send_file
from json import dumps
from loguru import logger
import yaml, uuid, base64, os, io
import pytesseract
import cv2
import subprocess
from subprocess import Popen
import time
from werkzeug.utils import secure_filename
import argparse
from easyocr import Reader

try:
    from PIL import Image
except ImportError:
    import Image

UPLOAD_FOLDER = './apps/static/uploads'

# Validating file extention
def allowed_file(image_file):
    logger.info("Validating file extention")
    return '.' in image_file and \
           image_file.rsplit('.', 1)[1].lower() in "png,jpg,pdf,tiff"

# Getting file extention
def getExtention(image_file):
    logger.info("Getting file extention")
    filename, file_extension = os.path.splitext(image_file)
    return filename, file_extension

def convert_to_tiff(image_file):
    logger.info("Converting pdf to tiff")
    converted_file_name = image_file.replace('pdf','tiff')
    p = subprocess.Popen('convert -density 300 '+ image_file +' -background white -alpha Off '+ converted_file_name , stderr=subprocess.STDOUT, shell=True)
    p_status = p.wait()
    time.sleep(5)
    if os.path.exists(image_file):
        os.remove(image_file)
    return converted_file_name


@blueprint.route('/index')
@login_required
def index():

    return render_template('home/index4.html', segment='index')

@blueprint.route('/ocr_tesseract')
@login_required
def ocr():

    return render_template('home/ocr_tesseract.html', segment='ocr_tesseract')

@blueprint.route('/ocr_easy')
@login_required
def easyocr():

    return render_template('home/ocr_easy.html', segment='ocr_easy')

@blueprint.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']

      # create a secure filename
      filename = secure_filename(f.filename)

      # save file to /static/uploads
      filepath = os.path.join(UPLOAD_FOLDER,filename)
      f.save(filepath)
      logger.info("reading file : " + filepath)
      # load the example image and convert it to grayscale
      image = cv2.imread(filepath)
      gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
      
      # apply thresholding to preprocess the image
      gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

      # apply median blurring to remove any blurring
      gray = cv2.medianBlur(gray, 3)

      # save the processed image in the /static/uploads directory
      ofilename = os.path.join(UPLOAD_FOLDER,"{}.png".format(os.getpid()))
      cv2.imwrite(ofilename, gray)
      
      # perform OCR on the processed image
      text = pytesseract.image_to_string(Image.open(ofilename), lang='kor+eng')
      # text = text.encode('utf-8')

      # print(text)
      
      # remove the processed image
      os.remove(ofilename)

      return render_template("home/uploaded.html", displaytext=text, fname=filename)


@blueprint.route('/easy_uploader', methods = ['GET', 'POST'])
def easyocr_upload_file():
   if request.method == 'POST':
      f = request.files['file']

      # create a secure filename
      filename = secure_filename(f.filename)

      # save file to /static/uploads
      filepath = os.path.join(UPLOAD_FOLDER,filename)
      f.save(filepath)
      logger.info("업로드한 파일Path : " + filepath)

      logger.info("OCR'ing input image...")
      langs = ['ko', 'en']

      reader = Reader(lang_list=langs, gpu=True)
      results = reader.readtext(filepath)
      logger.info("OCR결과 start ...")
      logger.info(results)
      logger.info("OCR결과 End")

      text = results

      return render_template("home/easyocr_uploaded.html", displaytext=text, fname=filename)

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
