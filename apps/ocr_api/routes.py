# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.ocr_api import blueprint
# -*- coding: utf-8 -*-
from flask import jsonify, request, abort
import urllib
import numpy as np
import cv2
from PIL import Image
import json

from apps.ocr_api.models import Document
# from .dto import DocumentDto

# api = DocumentDto.api # -> 모델 자체를 호출
# _document = DocumentDto.document # -> 모델의 각 칼럼을 호출

def url_to_image(url):
    """
    download the image, convert it to a NumPy array, and then read it into OpenCV format
    :param url: url to the image
    :return: image in format of Opencv
    """
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    print("url = ", url)
    # image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    image = cv2.imdecode(image, cv2.IMREAD_UNCHANGED)

    # image 크기 조정 with = 1346,height = 1732
    dim = (1400, 1550)
  
    # resize image
    resized = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

    return resized


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
        document = Document()
        data_json = json.loads(request.data)
        print("data_json=",data_json)
        document.doc_class = data_json['doc_class']
        document.image_url = data_json['image_url']
        image = url_to_image(document.image_url)
        print("image size : ", image.shape)
        json_object = document.execute_ocr(image)
        return jsonify(json_object)

    elif (request.content_type.startswith('multipart/form-data')):
        print("OCR multipart/form-data Start......")
        print("request={}".format(request))
        print("request.form={}".format(request.form))
        print("request.files={}".format(request.files['file']))
        document = Document()
        for key, value in request.form.items():
            print("data['{}']={}".format(key,value))
            if key == 'doc_class':
                document.doc_class = value
            elif key == 'image_url':
                document.image_url = value

        image_file = request.files['file']

        if image_file:
            image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
            print("image size : ", image.shape)
            # image = Image.open(image_file)
            json_object = document.execute_ocr(image)
            return jsonify(json_object)
        else:
            abort(401)
    else:
        return "415 Unsupported request Type ;)"





