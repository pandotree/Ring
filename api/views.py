# Create your views here.

import httplib2
from .models import Users, Groups
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.http import HttpResponse, Http404, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext
import json as simplejson
import social_auth.backends.google as google_auth

from social_auth import __version__ as version
from apiclient.discovery import build
from oauth2client.client import OAuth2Credentials
from oauth2client.client import AccessTokenCredentials
from social_auth.models import UserSocialAuth
from pprint import pprint

def index(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('index.html',context_instance=RequestContext(request)) #what does context_instance do?

def sign_in(request):
    if request.method != 'POST':
        return HttpResponseServerError("Bad request type: " + request.method)

    c = {}
    c.update(csrf(request)) # how does django keep track of our csrf tokens?

    username = request.POST['username']
    pw = request.POST['pw']

    user = authenticate(username=username, password=pw)
    if user is not None: # what is the difference between None and null?
        user = User.objects.get(username=username)
        user = Users.objects.get(user=user)
        request.session.__setitem__('logged_in', True)
        request.session.__setitem__('user_id', user.user_id)
        return HttpResponseRedirect("/dashboard/")

    return render_to_response('index.html',context_instance=RequestContext(request)) #eventually update ui with js that tells user to try again


def dashboard(request):
    logged_in = request.session.get('logged_in', False)
    if(not logged_in):
        return HttpResponse("Please log in!") #find a partial that we can render, or maybe redirect to homepage

    django_user = User.objects.get(username=request.POST['username'])
    ring_user = Users.objects.get(user=django_user)
    groups = ring_user.groups_set.all()
    if len(groups)==0:
        return render_to_response('dashboard.html',{'uncreated':True},context_instance=RequestContext(request))
    else:
        data = [{'name':group.group_name} for group in groups]
        response_json = simplejson.dumps(data)
        return render_to_response('dashboard.html',{'uncreated':False,'groups':groups},context_instance=RequestContext(request))
    
def create_user(request):
    if request.method != 'POST':
        return HttpResponseServerError("Bad request type: " + request.method)

    if 'email' not in request.POST:
        return HttpResponseServerError("No 'email' in POST")
    if 'pw' not in request.POST:
        return HttpResponseServerError("No 'pw' in POST")
    if 'confirm_pw' not in request.POST:
        return HttpResponseServerError("No 'confirm_pw' in POST")
    c = {}
    c.update(csrf(request))
    email = request.POST['email']
    pw = request.POST['pw']
    confirm_pw = request.POST['confirm_pw']

    if not pw == confirm_pw:
        return HttpResponseServerError("password does not match")

    user = User.objects.create_user(email, email, pw);
    django_user = Users(user=user, university="UPenn", phone_number=1112223333)
    django_user.save()
    #ring_user = Users(user=django_user) # what is the purpose of this line?

    response_json = simplejson.dumps({'email':email})
    return render_to_response('success.html', context_instance=RequestContext(request))

def create_group(request):
    if request.method != 'POST':
        return HttpResponseServerError("Bad request type: " + request.method)
    if 'group_name' not in request.POST:
        return HttpResponseServerError("No 'group_name' in POST")

    group_name = request.POST['group_name']
    user_id = request.session.get('user_id')

    user = Users.objects.get(user_id=user_id)
    django_group = Groups(group_name=group_name)
    django_group.save()
    django_group.users.add(user)

    return render_to_response('success.html', context_instance=RequestContext(request))

def show_docs(request):
    if request.method != 'GET':
        return HttpResponseServerError("Bad request type: " + request.method)
    http = httplib2.Http()
    instance = UserSocialAuth.objects.filter(provider='google-oauth2').get(user=request.user)

    token = instance.tokens['access_token']
    useragent = request.META['HTTP_USER_AGENT']
    credentials = AccessTokenCredentials(token, useragent)
    http = credentials.authorize(http)
    service = build('drive', 'v2', http=http)
    apirequest = service.files().list()
    while apirequest != None:
        response = apirequest.execute()
        for file in response.get('items', []):
            print repr(file.get('title')) + '\n'
        apirequest = service.files().list_next(apirequest, response)
    ctx = {
        'files': files
    }
    return render_to_response('documents.html', ctx, RequestContext(request))
