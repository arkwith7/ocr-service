# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.contrib.auth.forms import SetPasswordForm
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from .forms import LoginForm, SignUpForm
from .models import CustomUser
from apps.helpers import *
from apps import COMMON, helpers
from core.settings import GITHUB_AUTH, TWITTER_AUTH


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():

            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(username=username, password=password)

            # Credentials ok
            is_suspended = False
            if user:

                # Check Suspension state
                if user.status == COMMON.USER_SUSPENDED:
                    is_suspended = True
                    msg = 'Suspended account. Please contact support.'

                # All good
                else:

                    user.failed_logins = 0
                    user.save()
                    login(request, user)
                    return redirect("/")

            # Check user is registered
            user = username_exists(username)
            if not user:
                user = email_exists(username)
            # If user is suspended, don't check this case
            if not is_suspended:
                if user:

                    msg = 'Wrong password.'

                    # Update the fraud counter
                    user.failed_logins += 1

                    # Suspend the user (if needed)
                    if user.failed_logins > cfg_LOGIN_ATTEMPTS():
                        user.status = COMMON.USER_SUSPENDED
                        msg = 'Suspended account. Please contact support.'

                    # Update user
                    user.save()

                else:

                    msg = 'Username not registered.'

        else:
            msg = 'Error validating the form'
    else:
        msg = request.GET.get('message', None)

    return render(request, "accounts/login.html", {"form": form, "msg": msg,
                                                   "github_login": GITHUB_AUTH, "twitter_login": TWITTER_AUTH})


def register_user(request):

    msg     = None
    success = False

    # new Registration
    if request.method == "POST":
        form = SignUpForm(request.POST)
        
        if form.is_valid():
        
            form.save()
        
            username     = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            
            user         = authenticate(username=username, password=raw_password)

            msg = 'User created successfully.'
            success = True

            #return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


def change_password(request, **kwargs):

    form = SetPasswordForm(user=request.user, data=request.POST)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        message = 'Password successfully changed.'
        status = 200
    else:
        message = form.errors
        status = 400
    return JsonResponse({
        'message': message
    }, status=status)


def delete_account(request, **kwargs):
    result, message = helpers.delete_user(request.user.username)
    if not result:
        return JsonResponse({
            'errors': message
        }, status=400)
    logout(request)
    return HttpResponseRedirect('/login/')
