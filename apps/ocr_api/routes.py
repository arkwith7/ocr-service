# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.ocr_api import blueprint
# -*- coding: utf-8 -*-
from flask import jsonify, request, abort
import urllib
import numpy as np
import pytesseract
import cv2
import easyocr
import os

try:
    from PIL import Image
except ImportError:
    import Image

import json
import logging

# from .dto import DocumentDto

# api = DocumentDto.api # -> 모델 자체를 호출
# _document = DocumentDto.document # -> 모델의 각 칼럼을 호출

SECRET_KEY = os.getenv('SECRET_KEY', 'easyocr_vdt');
reader = easyocr.Reader(['ko','en'], gpu=False) # ['ja','en']

UPLOAD_FOLDER = './media/uploads'



def url_to_image(url):
    """
    download the image, convert it to a NumPy array, and then read it into OpenCV format
    :param url: url to the image
    :return: image in format of Opencv
    """
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    print("url = ", url)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image


def data_process(data):
    """
    read params from the received data
    :param data: in json format
    :return: params for image processing
    """
    doc_class = data["doc_class"]
    image_url = data["image_url"]
    secret_key = data["secret_key"]

    return doc_class, url_to_image(image_url), secret_key


def recognition(image):
    """
    :param image:
    :return:
    """
    results = []
    texts = reader.readtext(image)
    for (bbox, text, prob) in texts:
        output = {
            "coordinate": [list(map(float, coordinate)) for coordinate in bbox],
            "text": text,
            "score": prob
        }
        results.append(output)

    return results


@blueprint.route('/ocr', methods=['POST'])
def process():
    """
    received request from client and process the image
    :return: dict of width and points
    """
    print("request.headers={}".format(request.headers))
    print("request.content_type={}".format(request.content_type))
    print("request.headers['Content-Type']={}".format(request.headers['Content-Type']))
    if (request.content_type.startswith('application/json')):
        print("OCR application/json Start......")
        print("request={}".format(request))
        print("request.data={}".format(request.data))
        data_json = json.loads(request.data)
        print("data_json=",data_json)
        return jsonify(data_json)

    elif (request.content_type.startswith('multipart/form-data')):
        print("OCR multipart/form-data Start......")
        print("request={}".format(request))
        print("request.form={}".format(request.form))
        print("request.files={}".format(request.files['file']))
        for key, value in request.form.items():
            print("data['{}']={}".format(key,value))

        metadata = request.form
        # doc_class = metadata['doc_class']
        # image = metadata['image_url']
        # secret_key = metadata['secret_key']
        secret_key = 'easyocr_vdt'
        # return jsonify(metadata)
        # doc_class, image, secret_key = data_process(metadata)

        image_file = request.files['file']

        if image_file:
            image = Image.open(image_file)

        if secret_key == SECRET_KEY:
            results = recognition(image)
            return {
                "results": results
            }
        else:
            abort(401)
    else:
        return "415 Unsupported request Type ;)"





