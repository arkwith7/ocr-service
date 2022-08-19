# Create your models here.
from django.db import models
from django.utils import timezone
from django.conf import settings

from .exceptions import DuplicateDocumentNameError, DuplicateFolderNameError
from .managers import DocumentQuerySet, FolderManager, FolderQuerySet

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


class ImageFileManager(models.Manager):

    def search(self, query):
        return self.get_queryset().filter(models.Q(internal_reference__icontains=query) |
                                          models.Q(name__icontains=query) |
                                          models.Q(description__icontains=query)
                                          )


class ImageFile(models.Model):

    name = models.CharField("Name", max_length=100)
    internal_reference = models.CharField("Internal Reference", max_length=100, editable=False)
    biz_process = models.CharField("Business Process", max_length=200, null=True)
    doc_name = models.CharField("Document Name", max_length=200, null=True)
    ocr_engine = models.CharField("OCR Engine", max_length=50, default="Tesseract")
    description = models.TextField("Description", blank=True, null=True)
    image = models.ImageField(upload_to="", verbose_name="Input Image")
    create_at = models.DateTimeField("Create at", auto_now_add=True)
    updated_at = models.DateTimeField("Update at", auto_now=True)

    def __str__(self):
        return "{0:03d} - {1}".format(self.id, self.image)

    def execute_and_save_ocr(self):
        import time
        start_time = time.time()
        process_name = self.biz_process
        document_name = self.doc_name
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
        ocr_txt = OCRText(image = self, text = txt, biz_process=process_name, doc_name=document_name, lang = ocr_lang, ocr_engine = engine, execution_time = execution_time)
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
    biz_process = models.CharField("Business Process", max_length=200, null=True)
    doc_name = models.CharField("Document Name", max_length=200, null=True)
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

class Folder(models.Model):

    name = models.CharField(max_length=140)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE)

    objects = FolderManager.from_queryset(FolderQuerySet)()

    kind = "folder"
    icon = "folder-open"
    shared = None

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.pk and Folder.already_exists(self.name, self.parent):
            raise DuplicateFolderNameError(f"{self.name} already exists in this folder.")
        self.touch(self.author, commit=False)
        super().save(**kwargs)

class Document(models.Model):

    name = models.CharField(max_length=255)
    folder = models.ForeignKey(Folder, null=True, blank=True, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE)
    # file = models.FileField(upload_to=uuid_filename)
    original_filename = models.CharField(max_length=500)

    objects = DocumentQuerySet.as_manager()

    kind = "document"
    icon = "file"
    shared = None

    @classmethod
    def already_exists(cls, name, folder=None):
        return cls.objects.filter(name=name, folder=folder).exists()

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.pk and Document.already_exists(self.name, self.folder):
            raise DuplicateDocumentNameError(f"{self.name} already exists in this folder.")
        self.touch(self.author, commit=False)
        super().save(**kwargs)

    def unique_id(self):
        return "d-%d" % self.id
