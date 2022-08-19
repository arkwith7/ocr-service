
# coding: utf-8

# ### 운전면허증에서 문자 추출
# 네이버의 이미지에서 문자 오브젝트를 찾아내는 Craft와 Tesseract OCR을 이용해서 운전면허증에서 글자를 추출해 낸다.
# 
# Craft는 처음에 탬플리을 작성할때 이미지의 전체 글자 오브젝트의 좌표를 구하기 위해 사용하고,
# 
# Tesseract OCR는 각각의 인식된 글자 오브젝트 이미지에서 글자를 추출하기 위해 사용한다.
# 
# 1. 이미지를 읽어 들여 수직 수평 정렬하고 크기를 606, 960 크기로 재조정 한다.
# 2. 템플릿(Json포맷)을 읽어들이고 이미지에서 추출 대상 영역의 이미지를 잘라낸다.
# 3. 잘라내어진 이미지의 글자를 Tesseract OCR로 인식하고 출력 파일 Json파일을 생성한다.
# 
# [운전면허진위여부 조회](https://rankro.tistory.com/298)


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

def edge_detection(image_bgr):
    """
    흰색바탕의 A4크기의 배경에서 운전면허증 외곽 인식
    Input : image --> 이미지(bgr image)
    return : rot_rect --> 4개의 사각형 좌표와 기운 정도를 나타내는 각도 정보
    """

    ## (1) 이미지 이진화, 흰색부분을 검은색으로 면허증 부분은 흰색으로
    draw_image = image_bgr.copy()
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    binary = cv2.bitwise_not(gray)
    th, threshed = cv2.threshold(binary, 10, 255, cv2.THRESH_BINARY)

    ## (2) Find the max-area contour
    (_, contours,_) = cv2.findContours(threshed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # 면적이 큰거 5개만 추출
    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:2]

    screenCnt = None
    for index,c in enumerate(contours):
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # if our approximated contour has four points, then we
        # can assume that we have found our screen
        if len(approx) == 4:
            print("contour index==", index)
            screenCnt = approx
            ## This will extract the rotated rect from the contour
            rot_rect = cv2.minAreaRect(screenCnt)
            break

    if screenCnt is None:
        print("Do not find rectangle contour")
        rot_rect = None
    else:
        # show the contour (outline) of the piece of paper
        print ("Find rectangle contour")
        cv2.drawContours(draw_image, [screenCnt], -1, (0, 255, 0), 5)

    return rot_rect

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
    text = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', readData)
    #양쪽(위,아래)줄바꿈 제거
    text = text.rstrip('\n')
    text = text.rstrip('\r')
    text = text.rstrip('\r\n')
    text = text.rstrip()
    #양쪽(위,아래)스페이스 제거
    text = text.strip()
    #글자 중간에 있는 스페이스 제거
    text = text.replace(' ', '')
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

#OCR 엔진을 이용해서 운전면허증 템플릿 JSON과 문자 인식 대상 이미지를 입력으로 인식결과 JSON파일을 리턴한다.
def recognize_text(image_file, json_file):
    """
    OCR 엔진을 이용해서 운전면허증 템플릿 JSON과 문자 인식 대상 이미지를 입력으로 인식결과 JSON파일을 리턴한다.
    """
    # 주어진 file path 의 이미지 파일을 칼러 파일 BGR타입으로 읽어들인다.
    image_bgr = cv2.imread(image_file, cv2.IMREAD_COLOR)
    # RGB타입으로 변환
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    # 읽어 들인 파일의 양식(운전면허, 사업자등록증 등)의 외곽선을 감지한다.
    rect = edge_detection(image_bgr)
    bboxes = []
    if rect is not None:
        # 감지한 양식의 외곽선을 이용하여 기울어진 양식을 수평으로 정렬한다.
        warped_image = get_warpAffine(rect, image_rgb)
        # convert from openCV2 to PIL. Notice the COLOR_BGR2RGB which means that 
        # the color is converted from BGR to RGB
        color_coverted = cv2.cvtColor(warped_image, cv2.COLOR_BGR2RGB)
        print(color_coverted.shape)
        # 문자 인식율을 높이기 위해 이미지의 size(1800*1800), dpi(300) 정보를 확대 변경한다.
        change_image = change_image_dpi(color_coverted)
        print("change_image 이미지 shape :",change_image.shape)
        # 템플릿 적용을 위해 이미지 크기를 동일하게 가로 940, 세로 600 으로 재조정 한다.
        dst = cv2.resize(change_image, dsize=(940, 600), interpolation=cv2.INTER_AREA)
        print("dst 이미지 shape :",dst.shape)

        # 템플릿 JSON파일을 읽는다
        with open(json_file, 'r') as openfile: 
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
        bboxes, text_image_list = text_detection(dst, bboxes)

    # 이미지 크기를 (600, 940, 0)의 shape 정보를 이용하여 JSON에 입력
    height, width, _ = dst.shape
    json_object['meta']['imageSize']['height'] = height
    json_object['meta']['imageSize']['width'] = width
    
    # view the image with bounding boxes
    img_boxed = craft.show_bounding_boxes(dst, bboxes)

    # Tesseract OCR 엔진 config 정보 편집. 언어는 "kor+eng"
    language = json_object['meta']['language']
    custom_config = r'--psm 6'
    print(custom_config)
    # 인식대상 문자가 포함된 잘라낸 이미지 list 객체의 이미지를 하나씩 OCR 엔진을 이용 인식한 문자 정보를 되돌려 받는다.
    # 인식된 문자를 JSON에 입력한다.
    for cnt, text in enumerate(text_image_list, 1):
        # OCR 엔진에 입력으로 줄 이미지 크기를 2배 확대 한다.
#         higher_reso = cv2.resize(text,None,fx=1, fy=1, interpolation = cv2.INTER_CUBIC) #원본 이미지의 2배 사이즈
        threshold_image = thresholdImageText(text)
        # Tesseract OCR 엔진으로 부터 인식된 문자를 되돌려 받는다.
        result = pytesseract.image_to_string(threshold_image, lang=language, config=custom_config)
        clear_text = cleanText(result)
        text_box = bboxes[cnt-1].astype(int)
        if cnt == 1:
            # 1.생년월일
            json_object['drivers_license']['birthDate'] = clear_text
            json_object['meta']['annotations'][cnt-1]['text'] = clear_text

        elif cnt == 2:
            # 2.이름
            # hangul_name = re.sub('[^A-Za-z0-9가-힣]', '', string) 
            hangul_name = re.sub('[^가-힣]', '', clear_text)   
            json_object['drivers_license']['name'] = hangul_name
            json_object['meta']['annotations'][cnt-1]['text'] = hangul_name
        elif cnt == 3:
            # 3.면허번호
            result = pytesseract.image_to_string(text, lang=language, config=custom_config)
            clear_text = cleanText(result)
            licenseNum = re.sub('[^0-9가-힣]', '', clear_text)
            json_object['drivers_license']['licenseNum'] = licenseNum
            json_object['meta']['annotations'][cnt-1]['text'] = licenseNum
        elif cnt == 4:
            # 4.식별번호
            #clear_image = clearImageText(higher_reso)
            #tesseract sample.jpg stdout -l eng --oem 3 --psm 7 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            custom_config = r' -l eng --oem 3 --psm 7 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"'
            #custom_config = r' -l eng'
            result = pytesseract.image_to_string(threshold_image, config=custom_config)
            clear_text = cleanText(result)
            if len(clear_text) == 6:
                pass
            else:
                clear_text = ""
            json_object['drivers_license']['identificationNum'] = clear_text
            json_object['meta']['annotations'][cnt-1]['text'] = clear_text
        else:
            # Do the default
            print("번호[{}]={}, ".format(cnt,cleanText),text_box)

    return img_boxed, json_object

def main():
    """
    사용방법 : 이미지 파일 Path와 템플릿 json 파일을 인수로 준고 명령어 창(CMD)에서 실행한다
    python recognize_drivers_license.py ../zDoc/img/licence_card6.jpg drivers_licence_doc.json
    """
    for cnt, entry in enumerate(sys.argv):
        try:
            if cnt == 0:
                # 0번째 인수는 python file 이름이므로 pass
                pass
            elif cnt == 1:
                # 1번째 인수는 이미지 파일
                image_file = entry
            elif cnt == 2:
                # 2번째 인수는 운전면허증 템플릿 파일
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
