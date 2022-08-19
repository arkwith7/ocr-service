"""OCR_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.urls import path
from django.urls import path
from . import views
# app_name = 'general1' 

urlpatterns = [
    path('', views.index, name='index'),
    path('general_ocr/', views.general_ocr, name='general_ocr'),
    path('general_if/', views.general_if, name='general_if'),
    path('general_us/', views.general_us, name='general_us'),
    path('template_ml/', views.template_ml, name='template_ml'),
    # (?P<id>\d+)/$
    # url(r'detail_view/<id>', views.detail_view, name='detail_view' ), 
    path('detail_view/<id>', views.detail_view, name='detail_view' ), 
    # url(r'delete/<id>', views.delete, name='delete' ), 
    path('delete/(<id>', views.delete, name='delete' ), 
    path('about', views.about, name='about'),
    path('gettext', views.gettext, name='gettext'),
    # url(r'business_registration', views.business_registration, name='business_registration'),
    # url(r'detail_view2/(?P<id>\d+)/$', views.detail_view2, name='detail_view2' ), 
    # url(r'delete2/(?P<id>\d+)/$', views.delete2, name='delete2' ), 
]
