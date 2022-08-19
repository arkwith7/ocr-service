# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from apps                       import helpers
from apps.accounts.forms        import EditProfileForm
from apps.authentication.models import CustomUser
from apps                       import COMMON
from apps.helpers               import *


@login_required(login_url="/login/")
def user_list(request, **kwargs):

    # get all users
    if request.method == 'GET':
        users = CustomUser.objects.all()
        form = EditProfileForm()
        return render(request, 'accounts/user-list.html', context={
            'users': [
                {
                    'fullname': user.fullname,
                    'bio': user.bio,
                    'email': user.email,
                    'phone': user.phone,
                    'website': user.website,
                    'username': user.username,
                    'zipcode': user.zipcode,
                    'address': user.address,
                    'registration_date': user.registration_date,
                    'status': 0 if user.status == COMMON.USER_SUSPENDED else 1 ,
                    'image': user.image,
                }
                for user in users
            ],
            'form': form
        })

    # Update Profile    
    if request.method == 'POST':
        return profile(request, **kwargs)

    if request.method == 'PUT':
        user = CustomUser.objects.get(username=kwargs.get('username'))

        if user.status == COMMON.USER_ACTIVE:
            user.status = COMMON.USER_SUSPENDED
        else:
            user.status = COMMON.USER_ACTIVE

        user.failed_logins = 0
        user.save()
        return JsonResponse({})

    if request.method == 'DELETE':

        try:
            user = CustomUser.objects.filter(username=kwargs.get('username')).first()

            if user.is_superuser:
                raise Exception('Cannot delete superuser')

            user.delete()

        except Exception as e:
            return JsonResponse({
                'errors': str(e)
            }, status=400)
        return JsonResponse({})


@login_required(login_url="/login/")
def profile(request, **kwargs):

    if request.method == 'GET':
        user = CustomUser.objects.get(username=request.user.username)
        social_acc = user.socialaccount_set.first()

        if social_acc:
            user.image = social_acc.get_avatar_url()

        return render(request, 'accounts/user-profile.html', context={
            'user': {
                'fullname': user.fullname,
                'bio': user.bio,
                'email': user.email,
                'phone': user.phone,
                'website': user.website,
                'zipcode': user.zipcode,
                'address': user.address,
                'image': user.image,
                'username': user.username,
                'login_with_oauth': social_acc is not None,
                'provider': social_acc.provider if social_acc is not None else None
            }
        })

    if request.method == 'POST':

        form = EditProfileForm(request.POST, instance=CustomUser.objects.get(username=kwargs.get('username', request.user.username)))

        # Validate form
        if form.is_valid():

            user  = form.save()
            image = request.FILES.get('avatar-input', None)

            if cfg_FTP_UPLOAD() and image:

                try:
                    avatar_url = helpers.upload(user.username, image)
                    user.image = os.getenv("upload_url") + '/'.join(avatar_url.split("/")[-2:])
                    user.save()
                except Exception as e:
                    print(str(e))
                    print("There is a problem in connection with FTP")
                    return JsonResponse({
                        'errors': 'There is a problem in connection with FTP'
                    }, status=400)

            # All good        
            return JsonResponse({}, status=200)

        # We have validation errors,
        return JsonResponse({'errors': str( form.errors )}, status=400)

