from django import forms
from g_ocr.models import ImageFile
# , BusinessRegistrationImageFile


class ImageFileForm(forms.ModelForm):
    class Meta:
        model = ImageFile
        fields = ('ocr_engine', 'image',  )

# class BusinessRegistrationImageFileForm(forms.ModelForm):
#     class Meta:
#         model = BusinessRegistrationImageFile
#         fields = ('image', )
