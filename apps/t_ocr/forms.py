from django import forms
from t_ocr.models import ImageFile

class ImageFileForm(forms.ModelForm):
    class Meta:
        model = ImageFile
        fields = ('biz_process', 'doc_name', 'ocr_engine', 'image',  )

