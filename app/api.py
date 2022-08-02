from flask import Flask, request, jsonify
from flask_restx import Api, Resource, reqparse

from PIL import Image
import pytesseract

app = Flask(__name__)

api = Api(app, version='1.0', title='API 문서', description='Swagger 문서', doc="/api-docs")

ocr_api = api.namespace('OCR', description='OCR API')

@ocr_api.route('/')
class TESSERACT_OCR(Resource):
    def POST(self):
        if 'image' not in request.files:
            return jsonify(
                error={
                    'image': 'This field is required.'
                }
            ), 400

        image = Image.open(request.files['image'])

        image_text = pytesseract.image_to_string(
            image,
            lang='kor+eng'
        )

        return jsonify({
            'text': image_text
        })

@ocr_api.route('/hello')  # 데코레이터 이용, '/hello' 경로에 클래스 등록
class HelloWorld(Resource):
    def get(self):  # GET 요청시 리턴 값에 해당 하는 dict를 JSON 형태로 반환
        return {"hello": "world!"}

# @app.route('/', methods=['POST'])
# def index():
#     if 'image' not in request.files:
#         return jsonify(
#             error={
#                 'image': 'This field is required.'
#             }
#         ), 400

#     image = Image.open(request.files['image'])

#     image_text = pytesseract.image_to_string(
#         image,
#         lang='kor+eng'
#     )

#     return jsonify({
#         'text': image_text
#     })

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)