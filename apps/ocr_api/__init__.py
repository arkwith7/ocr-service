# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from flask import Blueprint
from flask_cors import CORS
# from flask_restx import Api
# from flask_restplus import Api
# from .routes import api as docs_ns

blueprint = Blueprint(
    'ocr_api_blueprint',
    __name__,
    url_prefix=''
)
CORS(blueprint)
# api = Api(blueprint,
#           title='수출입문서 OCR API 서버',
#           version='1.0',
#           description='SMBC 수출입문서 OCR'
#           )
 
# api.add_namespace(docs_ns, path='/v1/ocr-api')
