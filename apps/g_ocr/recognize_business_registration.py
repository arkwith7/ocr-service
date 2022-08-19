# coding: utf-8

# ### 사업자등록증 이미지에서 글자 추출
# 네이버의 이미지에서 문자 오브젝트를 찾아내는 Craft와 Tesseract OCR을 이용해서 사업자등록증 이미지에서 글자를 추출해 낸다.
# 
# Craft는 처음에 탬플리을 작성할때 이미지의 전체 글자 오브젝트의 좌표를 구하기 위해 사용하고,
# 
# Tesseract OCR는 각각의 인식된 글자 오브젝트 이미지에서 글자를 추출하기 위해 사용한다.
# 
# 1. 이미지를 읽어 들여 수직 수평 정렬하고 크기를 606, 960 크기로 재조정 한다.
# 2. 템플릿(Json포맷)을 읽어들이고 이미지에서 추출 대상 영역의 이미지를 잘라낸다.
# 3. 잘라내어진 이미지의 글자를 Tesseract OCR로 인식하고 출력 파일 Json파일을 생성한다.
# 
# [사업자등록상태조회](https://teht.hometax.go.kr/websquare/websquare.html?w2xPath=/ui/ab/a/a/UTEABAAA13.xml)


import sys
import datetime
import tempfile
import re
import math
import json
import craft
import cv2
from PIL import Image
import imutils
import numpy as np
import matplotlib.pyplot as plt
import pytesseract
from pytesseract import Output

# Crop Rectangle returned by minAreaRect OpenCV [Python]
# https://stackoverflow.com/questions/37177811/crop-rectangle-returned-by-minarearect-opencv-python
def get_warpAffine(rect, img):
    """
    Input : rect(cv2.minAreaRect()), img
    rect : 4개의 사각형 좌표와 기운 정도를 나타내는 각도 정보
    img : 칼라 이미지(Color image)
    return : croppedRotated
    사각형 좌표로 잘라내고 기운 각도가 없는 수평정렬된 이미지
    Procedure :
    1. 좌표와 이미지를 입력받아 좌표와 각도 분리
    2. 좌표내의 이미지를 수평이 되도록 변환
    3. 좌표의 크기대로 이미지를 자르고 리턴한다.
    """
    box = cv2.boxPoints(rect) 
    box = np.int0(box)

    W = rect[1][0]
    H = rect[1][1]

    Xs = [i[0] for i in box]
    Ys = [i[1] for i in box]
    x1 = min(Xs)
    x2 = max(Xs)
    y1 = min(Ys)
    y2 = max(Ys)

    angle = rect[2]
    if angle < -45:
        angle += 90

    # Center of rectangle in source image
    center = ((x1+x2)/2,(y1+y2)/2)
    # Size of the upright rectangle bounding the rotated rectangle
    size = (x2-x1, y2-y1)
    M = cv2.getRotationMatrix2D((size[0]/2, size[1]/2), angle, 1.0)
    # Cropped upright rectangle
    cropped = cv2.getRectSubPix(img, size, center)
    cropped = cv2.warpAffine(cropped, M, size)
    croppedW = H if H > W else W
    croppedH = H if H < W else W
    # Final cropped & rotated rectangle
    croppedRotated = cv2.getRectSubPix(cropped, (int(croppedW),int(croppedH)), (size[0]/2, size[1]/2))
    
    return croppedRotated

# Preprocessing image for Tesseract OCR with OpenCV
# https://stackoverflow.com/questions/28935983/preprocessing-image-for-tesseract-ocr-with-opencv/42125962
def change_image_dpi(image,IMAGE_SIZE = 1800):
    """
    Pillow (필로우- 이미지 처리)를 활용
    입력 이미지를 (1800, 1800)에 300dpi 이미지로 변경
    """
#     im = Image.open(file_path)
    im=Image.fromarray(image)
    length_x, width_y = im.size
    factor = max(1, int(IMAGE_SIZE / length_x))
    size = factor * length_x, factor * width_y
    print("change_image_dpi 이미지 size=={}".format(size))
    # size = (1800, 1800)
    # 사업자등록증 가로 * 세로 크기 고정
    size = (1654, 2340)
    im_resized = im.resize(size, Image.ANTIALIAS)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    temp_filename = temp_file.name
    im_resized.save(temp_filename, dpi=(300, 300))
    image_bgr = cv2.imread(temp_filename, cv2.IMREAD_COLOR)
    return image_bgr


def text_detection(image_bgr, bboxes=None):
    """
    이미지를 입력받아 문자가 있는 영역을 인식하고 잘라내어 list객체로 리턴한다.
    """

    # run the detector
    if bboxes is None:
        bboxes, polys, heatmap = craft.detect_text(image_bgr) 
    # view the image with bounding boxes
    #img_boxed = craft.show_bounding_boxes(image_rgb, bboxes)
    # cv2.imshow('fig', img_boxed)
    # view detection heatmap
    # cv2.imshow('fig', heatmap)
    detected_text = []
    for orig_box in bboxes:
        # get rotated rectangle from contour
        rot_rect = cv2.minAreaRect(orig_box)
        text = get_warpAffine(rot_rect, image_bgr)
        detected_text.append(text)
        
    return bboxes, detected_text

#텍스트 정제(전처리)
def cleanText(readData):
    #스팸 메세지에 포함되어 있는 특수 문자 제거
#     text = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', readData)
    text = re.sub('[=+#/\?:^$.@*\"※~&%ㆍ!』\\‘|\[\]\<\>`\'…》]}', '', readData)
    #양쪽(위,아래)줄바꿈 제거
    text = text.rstrip('\n')
    text = text.rstrip('\r')
    text = text.rstrip('\r\n')
    text = text.rstrip()
    #양쪽(위,아래)스페이스 제거
    text = text.strip()
    #글자 중간에 있는 스페이스 제거
#     text = text.replace(' ', '')
    return text

#OCR전 이미지 이진화(전처리)
def thresholdImageText(image):
    """
    이미지의 배경은 흰색으로 글자는 검정색으로 처리
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    return thresh

#OCR전 이미지 밝게처리(전처리)
def clearImageText(image):
    """
    이미지의 글자부분이 조금더 선명하도록 처리
    """
    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3., tileGridSize=(8,8))
    
    # convert from BGR to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    # split on 3 different channels
    l, a, b = cv2.split(lab)    
    # apply CLAHE to the L-channel
    l2 = clahe.apply(l) 
    # merge channels
    lab = cv2.merge((l2,a,b))
    # convert from LAB to BGR
    image2 = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)  
    
    return image2

#OCR 엔진을 이용해서 사업자등록증 템플릿 JSON과 문자 인식 대상 이미지를 입력으로 인식결과 JSON파일을 리턴한다.
def recognize_text(image_file, json_file):
    """
    OCR 엔진을 이용해서 사업자등록증 템플릿 JSON과 문자 인식 대상 이미지를 입력으로 인식결과 JSON파일을 리턴한다.
    """
    # 주어진 file path 의 이미지 파일을 칼러 파일 BGR타입으로 읽어들인다.
    image_bgr = cv2.imread(image_file, cv2.IMREAD_COLOR)
    # RGB타입으로 변환
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

#     # 읽어 들인 파일의 양식(운전면허, 사업자등록증 등)의 외곽선을 감지한다.
#     rect = edge_detection(image_bgr)
    bboxes = []

    change_image = change_image_dpi(image_bgr)
    print("change_image 이미지 shape :",change_image.shape)

    # 템플릿 JSON파일을 읽는다
    with open(json_file, 'r', encoding='utf-8') as openfile:
        # Reading from json file 
        json_object = json.load(openfile) 

    # 템플릿 JSON파일에서 레이블별로 문자를 인식할 대상 영역정보(좌표)을 읽는다
    for data in json_object['meta']['annotations']:
        # python의 list객체를 numpy의 array type으로 변환
        # bboxes = np.array(bboxes)
        bboxes.append(np.array(data['boundingBox']))

    # 레이블별로 문자를 인식할 대상 영역정보(좌표)와 이미지 정보를 입력하고 
    # 인식대상 문자가 포함된 잘라낸 이미지 list 객체와 좌표정보를 되돌려 받는다.
    # 좌표정보를 주지 않으면 이미지에서 인식 가능한 문자가 포함된 모든 영역 좌표 정보를 되돌려 준다.
    bboxes, text_image_list = text_detection(change_image, bboxes)


    # 이미지 크기를 (600, 940, 0)의 shape 정보를 이용하여 JSON에 입력
    height, width, _ = change_image.shape
    json_object['meta']['imageSize']['height'] = height
    json_object['meta']['imageSize']['width'] = width
    
    # view the image with bounding boxes
    img_boxed = craft.show_bounding_boxes(image_rgb, bboxes)

    # Tesseract OCR 엔진 config 정보 편집. 언어는 "kor+eng"
    language = json_object['meta']['language']
    custom_config = r'--psm 6'
    print(custom_config)
    # 인식대상 문자가 포함된 잘라낸 이미지 list 객체의 이미지를 하나씩 OCR 엔진을 이용 인식한 문자 정보를 되돌려 받는다.
    # 인식된 문자를 JSON에 입력한다.
    for cnt, text in enumerate(text_image_list, 1):
        # OCR 엔진에 입력으로 줄 이미지 크기를 2배 확대 한다.
        threshold_image = thresholdImageText(text)
        # Tesseract OCR 엔진으로 부터 인식된 문자를 되돌려 받는다.
        result = pytesseract.image_to_string(threshold_image, lang=language, config=custom_config)
        clear_text = cleanText(result)
        text_box = bboxes[cnt-1].astype(int)
        if cnt == 1:
            # 1.등록번호(사업자번호)
#             identificationNum = re.sub('[^0-9가-힣]', '', clear_text)
            identificationNum = clear_text.replace(' ', '')
            json_object['license']['identificationNum'] = identificationNum
            json_object['meta']['annotations'][cnt-1]['text'] = identificationNum

        elif cnt == 2:
            # 2.법인명(단체명)
            # hangul_name = re.sub('[^A-Za-z0-9가-힣]', '', string) 
#             hangul_name = re.sub('[^A-Za-z0-9가-힣]', '', clear_text)   
            json_object['license']['companyName'] = clear_text
            json_object['meta']['annotations'][cnt-1]['text'] = clear_text
        elif cnt == 3:
            # 3.대표자
            representativeName = re.sub('[^A-Za-z가-힣]', '', clear_text)
            json_object['license']['representativeName'] = representativeName
            json_object['meta']['annotations'][cnt-1]['text'] = representativeName
        elif cnt == 4:
            # 4.개업년월일
            json_object['license']['establishmentDate'] = clear_text
            json_object['meta']['annotations'][cnt-1]['text'] = clear_text
        elif cnt == 5:
            # 5.법인등록번호
            json_object['license']['regNum'] = clear_text
            json_object['meta']['annotations'][cnt-1]['text'] = clear_text
        elif cnt == 6:
            # 6.사업장소재지
            location = re.sub('\n', '', clear_text)
            json_object['license']['location'] = location
            json_object['meta']['annotations'][cnt-1]['text'] = location
        elif cnt == 7:
            # 7.본점소재지
            hqLocation = re.sub('}', '', clear_text)
            hqLocation = re.sub('\n', '', hqLocation)
            json_object['license']['hqLocation'] = hqLocation
            json_object['meta']['annotations'][cnt-1]['text'] = hqLocation
        elif cnt == 8:
            # 8.업태
            bizType = clear_text.split('\n')
            json_object['license']['bizType'] = bizType[0]
            json_object['meta']['annotations'][cnt-1]['text'] = bizType[0]
        elif cnt == 9:
            # 9.종목
            bizItem = clear_text.split('\n')
            json_object['license']['bizItem'] = bizItem[0]
            json_object['meta']['annotations'][cnt-1]['text'] = bizItem[0]
        elif cnt == 10:
            # 10.사업자구분
            json_object['license']['taxpayerType'] = clear_text
            json_object['meta']['annotations'][cnt-1]['text'] = clear_text
        else:
            # Do the default
            print("번호[{}]={}, ".format(cnt,cleanText),text_box)

    return img_boxed, json_object


def main():
    """
    예로서 명령어 창에서 아래와 같이 입력하면 글자인식영역표시 사업자등록증 이미지 파일과 인식한 글자를 포함하는 Json파일을
    작업디렉토리에 출력한다.
    python recognize_business_registration.py ../zDoc/img/BusinessRegistration02.jpg BusinessRegistration01_doc.json 
    """
    for cnt, entry in enumerate(sys.argv):
        try:
            if cnt == 0:
                # 0번째 인수는 python file 이름이므로 pass
                pass
            elif cnt == 1:
                # 1번째 인수는 이미지 파일(jpg, png)
                image_file = entry
            elif cnt == 2:
                # 2번째 인수는 사업자등록증 템플릿 파일(json)
                json_file = entry
            else:
                # 기타 인수는 무시
                break
        except Exception as e:
            print("Oops!", e.__class__, "occurred.")
            print("Can not recognize text....")
            print()
            
    img_boxed, json_object = recognize_text(image_file, json_file)
    
    # 파일 이름 작명을 위한 datetime 획득
    timestamp = datetime.datetime.now()
    timestamp_str = re.sub('[-:. ]', '', str(timestamp))

    # 인식한 부분의 글자를 박스로 표시한 이미지를 저장
    img_filename = timestamp_str + '.jpg'
    cv2.imwrite(img_filename, img_boxed)
    print("boxed filename=[{}]".format(img_filename))
    
    # 인식한 결과 텍스트가 정리된 JSON 파일 저장
    json_filename = timestamp_str + '.json'
    with open(json_filename, "w", encoding='utf-8') as outfile:
        json.dump(json_object, outfile, ensure_ascii=False) 

    print("json filename=[{}]".format(json_filename))

if __name__ == "__main__":
    main()
