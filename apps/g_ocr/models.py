from django.db import models
from django.conf import settings

# Create your models here.
import os
from . import utils
import hashlib
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

from easyocr import Reader
import cv2
import numpy as np

# 사업자등록증 문자인식 기능 삽입
# from . import recognize_business_registration

class ImageFileManager(models.Manager):

    def search(self, query):
        return self.get_queryset().filter(models.Q(internal_reference__icontains=query) |
                                          models.Q(name__icontains=query) |
                                          models.Q(description__icontains=query)
                                          )


class ImageFile(models.Model):

    name = models.CharField("Name", max_length=100)
    internal_reference = models.CharField("Internal Reference", max_length=100, editable=False)
    ocr_engine = models.CharField("OCR Engine", max_length=50, default="Tesseract")
    description = models.TextField("Description", blank=True, null=True)
    image = models.ImageField(upload_to="OCR_image/input/", verbose_name="Input Image")
    create_at = models.DateTimeField("Create at", auto_now_add=True)
    updated_at = models.DateTimeField("Update at", auto_now=True)

    def __str__(self):
        return "{0:03d} - {1}".format(self.id, self.image)

    def execute_and_save_ocr(self):
        import time
        start_time = time.time()
        engine = self.ocr_engine
        img = Image.open(self.image)
        print("이미지 파일 패쓰",self.image)

        print("[INFO] OCR'ing input image...")
        txt = ""
        ocr_lang = ""
        if engine == "EasyOCR":
            opencvImage = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            # EasyOCR 적용
            langs = ['ko', 'en']
            for lang in langs:
                ocr_lang += lang + ','

            reader = Reader(lang_list=langs, gpu=True)
            txt_list = reader.readtext(opencvImage, detail = 0, paragraph=True)

            for text in txt_list:
                txt += text + "\r\n"

        elif engine == "Tesseract":
            # added by phs for windows 10 tesseract-ocr-w64-setup-v5.0.0-alpha.20200328
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

            # # utf8_txt = bytes(txt, encoding="UTF-8")
            # # txt = pytesseract.image_to_string(img, lang='kor')            
            ocr_lang = 'kor+eng'
            txt = pytesseract.image_to_string(img, lang=ocr_lang)
            




        execution_time = time.time() - start_time
        ocr_txt = OCRText(image = self, text = txt, lang = ocr_lang, ocr_engine = engine, execution_time = execution_time)
        ocr_txt.save()
        # save a text file
        # filename = os.path.abspath(os.path.dirname(__file__))+"/sample.txt"
        # f = open(filename, "a")
        # f.truncate(0)
        # f.write(txt)
        # f.close()

        print("The image {0} was opened.".format(self.image))
        print('OCR: \n{0}\n'.format(txt))
        print('Execution Time: {0}'.format(ocr_txt.execution_time))

        return ocr_txt

    """
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('course_details', args=[], kwargs={'slug': self.slug})
    """

    def save(self, *args, **kwargs):

        if not self.internal_reference:
            random_value = utils.random_value_generator(size=20)
            while ImageFile.objects.filter(internal_reference=random_value).exists():
                random_value = utils.random_value_generator(size=20)
            hash_value = hashlib.md5(bytes(str(self.id) + str(random_value), 'utf-8'))
            self.internal_reference = hash_value.hexdigest()
        super(ImageFile, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "ImageFile"
        verbose_name_plural = "ImageFiles"
        ordering = ['id']

    objects = ImageFileManager()


class OCRText(models.Model):
    text = models.TextField("OCR text", blank=True)
    ocr_engine = models.CharField("OCR Engine", max_length=50, default="Tesseract")
    lang = models.TextField("Language", default="kor+eng")
    execution_time = models.IntegerField("Execution Time", editable=False, null=True);
    image = models.ForeignKey('ImageFile', on_delete=models.CASCADE)
    create_at = models.DateTimeField("Create at", auto_now_add=True)
    updated_at = models.DateTimeField("Update at", auto_now=True)

    def __str__(self):
        return "{0:03d} - {1}".format(self.id, self.image.internal_reference)

    class Meta:
        verbose_name = "OCRText"
        verbose_name_plural = "OCRTexts"
        ordering = ['id']

# class BusinessRegistrationImageFile(models.Model):

#     name = models.CharField("Name", max_length=100)
#     internal_reference = models.CharField("Internal Reference", max_length=100, editable=False)
#     description = models.TextField("Description", blank=True, null=True)
#     image = models.ImageField(upload_to="OCR_image/input/", verbose_name="A4 크기의 사업자등록증 이미지 파일을 선택하세요.")
#     create_at = models.DateTimeField("Create at", auto_now_add=True)
#     updated_at = models.DateTimeField("Update at", auto_now=True)

#     def __str__(self):
#         return "{0:03d} - {1}".format(self.id, self.image)

#     def execute_and_save_ocr(self):
#         import time
#         start_time = time.time()

#         # img = Image.open(self.image)
#         image_file = settings.MEDIA_ROOT + "/" + self.image.name # 'img/BusinessRegistration02.jpg'
#         print("The image {0} was opened.".format(image_file))
#         current_work_dir = os.path.dirname(os.path.realpath(__file__))
#         json_file = os.path.join(current_work_dir, 'BusinessRegistration01_doc.json') # 'BusinessRegistration01_doc.json'
#         print("The json file path is {0}.".format(json_file))
#         # added by phs for windows 10 tesseract-ocr-w64-setup-v5.0.0-alpha.20200328
#         # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


#         img_boxed, json_object = recognize_business_registration.recognize_text(image_file, json_file)
#         ocr_lang = json_object['meta']['language']
#         execution_time = time.time() - start_time
#         ocr_txt = BusinessRegistrationOCRText(image = self, text = json_object, lang = ocr_lang, execution_time = execution_time)
#         ocr_txt.save()


#         print('BusinessRegistrationOCR: \n{0}\n'.format(json_object))
#         print('Execution Time: {0}'.format(ocr_txt.execution_time))

#         return ocr_txt

#     """
#     def get_absolute_url(self):
#         from django.urls import reverse
#         return reverse('course_details', args=[], kwargs={'slug': self.slug})
#     """

#     def save(self, *args, **kwargs):

#         if not self.internal_reference:
#             random_value = utils.random_value_generator(size=20)
#             while BusinessRegistrationImageFile.objects.filter(internal_reference=random_value).exists():
#                 random_value = utils.random_value_generator(size=20)
#             hash_value = hashlib.md5(bytes(str(self.id) + str(random_value), 'utf-8'))
#             self.internal_reference = hash_value.hexdigest()
#         super(BusinessRegistrationImageFile, self).save(*args, **kwargs)

#     class Meta:
#         verbose_name = "BusinessRegistrationImageFile"
#         verbose_name_plural = "BusinessRegistrationImageFiles"
#         ordering = ['id']

#     objects = ImageFileManager()

# class BusinessRegistrationOCRText(models.Model):
#     text = models.TextField("OCR text", blank=True)
#     lang = models.TextField("Language", default="kor+eng")
#     execution_time = models.IntegerField("Execution Time", editable=False, null=True);
#     image = models.ForeignKey('BusinessRegistrationImageFile', on_delete=models.CASCADE)
#     create_at = models.DateTimeField("Create at", auto_now_add=True)
#     updated_at = models.DateTimeField("Update at", auto_now=True)

#     def __str__(self):
#         return "{0:03d} - {1}".format(self.id, self.image.internal_reference)

#     class Meta:
#         verbose_name = "BusinessRegistrationOCRText"
#         verbose_name_plural = "BusinessRegistrationOCRTexts"
#         ordering = ['id']

