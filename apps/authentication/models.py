# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps import COMMON

# Create your models here.

class CustomUser(AbstractUser):

    failed_logins     = models.IntegerField(default=0)
    status            = models.IntegerField(default=COMMON.USER_ACTIVE)  
    website           = models.URLField(default='', blank=True)
    phone             = models.CharField(max_length=20,default='', blank=True)
    registration_date = models.DateField(auto_now=True)
    fullname          = models.CharField(max_length=50, default='', blank=True)
    address           = models.TextField(default='', blank=True)
    zipcode           = models.CharField(max_length=10, default='', blank=True)
    bio               = models.TextField(default='', blank=True)
    image             = models.URLField(default='')


