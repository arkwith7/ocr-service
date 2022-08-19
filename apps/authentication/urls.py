# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, include
from .views import login_view, register_user, change_password, delete_account
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change_password/", change_password, name="change-password"),
    path("delete_account/", delete_account, name="delete-account"),
    path('social_login/', include('allauth.urls')),

]
