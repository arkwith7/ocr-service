# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from . import views
app_name = 'template' 

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('annotation/', views.annotation, name='annotation'),
    path('t_ocr_view/<id>', views.t_ocr_view, name='t_ocr_view' ), 
    # url(r'delete/<id>', views.delete, name='delete' ), 
    path('t_ocr_delete/<id>', views.t_ocr_delete, name='t_ocr_delete' ), 
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
