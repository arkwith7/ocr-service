from django.shortcuts import render, get_object_or_404, HttpResponseRedirect # added

# Create your views here.
import os
from django.http import HttpResponse
from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from g_ocr.forms import ImageFileForm
# , BusinessRegistrationImageFileForm
from g_ocr.models import ImageFile, OCRText
# , BusinessRegistrationImageFile, BusinessRegistrationOCRText
import ast
import json

def index(request):

    return render(request, 'dashboard-text-recog.html')

def general_ocr(request):
    # print("general_ocr list start...")
    data = dict()
    image_form = ImageFileForm(request.POST or None, request.FILES or None)
    # print("image_form : ",image_form)
    # print("image_form.is_valid():[{}]".format(image_form.is_valid()))
    # print("image_form.ocr_engine:[{}]".format(image_form.ocr_engine))
    if image_form.is_valid():
        # print("general_ocr enroll start...")
        image = image_form.save()
        image.execute_and_save_ocr()
        print("ImageFileModel.id:[{}]".format(image.id))
        print("ImageFileModel.image:[{}]".format(image.image))
        print("ImageFileModel.ocr_engine:[{}]".format(image.ocr_engine))
        # dictionary for initial data with  
        # field names as keys 
        context ={} 
    
        # add the dictionary during initialization 
        context["data"] = ImageFile.objects.get(id = image.id) 
        return render(request, 'result.html', context=context)

    image_list = ImageFile.objects.all().order_by('-id')
    page = request.GET.get('page', 1)

    data['image_form'] = image_form
    # data['image_list'] = image_list

    paginator = Paginator(image_list, 3)
    try:
        data['image_list'] = paginator.page(page)
    except PageNotAnInteger:
        data['image_list'] = paginator.page(1)
    except EmptyPage:
        data['image_list'] = paginator.page(paginator.num_pages)

    return render(request, "general_ocr.html", data)

def general_if(request):
    return render(request, "general_if.html")
def general_us(request):
    return render(request, "general_us.html")

def template_ml(request):
    return render(request, "template_ml.html")

def about(request):
    return render(request, 'about.html')

# pass id attribute from urls 
def detail_view(request, id): 
    # dictionary for initial data with  
    # field names as keys 
    print("....start detail_view")
    context ={}   
    # add the dictionary during initialization
    context["data"] = OCRText.objects.get(id = id)
    print("context[data]:[{}]".format(context["data"]))
    print("context[data.image]:[{}]".format(context["data"].image))
    print("context[data.image.id]:[{}]".format(context["data"].image.id))
    print("context[data.image.image]:[{}]".format(context["data"].image.image))
    print("context[data.lang]:[{}]".format(context["data"].lang))
    print("context[data.text]:[{}]".format(context["data"].text))
    # save a text file
    # filename = os.getcwd()+"/sample.txt"
    # filename = os.path.abspath(os.path.dirname(__file__))+"/sample.txt"
    # utf8_txt = bytes(context["data"].text, encoding="UTF-8")
    # print("sample.txt : ", filename)
    # f = open(filename, "a")
    # f.truncate(0)
    # f.write(context["data"].text).encode('utf-8').strip()
    # f.close()
    context["data"] ={
        "image" : context["data"].image.image,
        "ocr_text" : context["data"].text
    }   
          
    return render(request, 'detail.html', context) 

def delete(request, id):
    # fetch the object related to passed id 
    obj = get_object_or_404(ImageFile, id = id) 
    # delete object 
    obj.delete() 
    # after deleting redirect to  
    # home page 
    return HttpResponseRedirect("/ocr/general_ocr/") 

def gettext(request):

    filename = os.path.abspath(os.path.dirname(__file__))+"/sample.txt"
    with open(filename) as fp:
        src = fp.read()

    # some code
    response = HttpResponse(src, content_type='application/text charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="sample.txt"'

    return response

# def business_registration(request):
#     data = dict()

#     image_form = BusinessRegistrationImageFileForm(request.POST or None, request.FILES or None)
#     if image_form.is_valid():
#         image = image_form.save()
#         image.execute_and_save_ocr()
#         # print("ImageFileModel.id:[{}]".format(image.id))
#         # print("ImageFileModel.image:[{}]".format(image.image))
#         # dictionary for initial data with  
#         # field names as keys 
#         context ={} 
    
#         # add the dictionary during initialization 
#         context["data"] = BusinessRegistrationImageFile.objects.get(id = image.id) 
#         return render(request, 'tesseract_ocr/business_registration_result.html', context=context)

#     image_list = BusinessRegistrationImageFile.objects.all().order_by('-id')
#     page = request.GET.get('page', 1)

#     data['image_form'] = image_form
#     # data['image_list'] = image_list

#     paginator = Paginator(image_list, 3)
#     try:
#         data['image_list'] = paginator.page(page)
#     except PageNotAnInteger:
#         data['image_list'] = paginator.page(1)
#     except EmptyPage:
#         data['image_list'] = paginator.page(paginator.num_pages)

#     return render(request, 'tesseract_ocr/business_registration.html', data)

# def detail_view2(request, id): 
#     # dictionary for initial data with  
#     # field names as keys 
#     print("... starting business_registration_detail_view")
#     context ={}
#     # json_data = {}   
#     # add the dictionary during initialization
#     # context["data"] = BusinessRegistrationImageFile.objects.get(id = id)
#     context["data"] = BusinessRegistrationOCRText.objects.get(image_id = id)
#     # print("context[data]:[{}]".format(context["data"].businessregistrationocrtext_set.last))
#     # print("context[data.text]:[{}]".format(context["data"].text))
#     license_data = ast.literal_eval(context["data"].text)
#     # license_data = json.loads(license_data)
#     print("json_data type:{}".format(type(license_data)))
#     # print("license_data:{}".format(license_data))
#     # print("license_data['license']:[{}]".format(license_data["license"]))
#     context["data"] ={
#         "image" : context["data"].image.image,
#         "ocr_text" : license_data["license"]
#     }   
          
#     return render(request, 'tesseract_ocr/business_registration_result.html', context) 

# def delete2(request, id):
#     # fetch the object related to passed id 
#     print("... starting business_registration_delete")
#     obj = get_object_or_404(BusinessRegistrationImageFile, id = id) 
#     # delete object 
#     obj.delete() 
#     # after deleting redirect to  
#     # home page 
#     return HttpResponseRedirect("/ocr/business_registration/") 
