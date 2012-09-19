# Create your views here.

from .models import RichUser, Group, MessageThread, Message, PinnedItem, GroupCode
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.mail import EmailMessage
from django.http import HttpResponse, Http404, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from django.template import RequestContext

from apiclient.discovery import build
from bs4 import BeautifulSoup # an HTML parser
from itertools import groupby
from oauth2client.client import OAuth2Credentials
from oauth2client.client import AccessTokenCredentials
from pprint import pprint
from social_auth import __version__ as version
import social_auth.backends.google as google_auth
from social_auth.models import UserSocialAuth
from twilio.rest import TwilioRestClient

import os
import string
import datetime
import httplib2
import requests
import urllib

# apparently this is good practice
try: import simplejson as json
except ImportError: import json

def index(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('index.html',context_instance=RequestContext(request)) #what does context_instance do?

def group_signup(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('group-signup.html',context_instance=RequestContext(request)) 

def sign_in(request):
    if request.method != 'POST':
        return HttpResponseServerError("Bad request type: " + request.method)

    c = {}
    c.update(csrf(request)) # how does django keep track of our csrf tokens?

    username = request.POST['username']
    pw = request.POST['pw']

    user = authenticate(username=username, password=pw)
    if user is not None: # returns None if the password is invalid (what is the difference between None and null?)
        try:
            ring_user = RichUser.objects.get(user=user)
        except RichUser.DoesNotExist: # sanity check, this should never happen under normal use cases. potentially refactor to get_object_or_404 and catch the http404 exception
            return HttpResponse("Oops, looks like you haven't created an account with us yet!") 
        request.session.__setitem__('logged_in', True)
        request.session.__setitem__('user_id', ring_user.user_id)
        return HttpResponseRedirect('/dashboard/')
    else:
        return HttpResponse('Your username and password were incorrect') #eventually update ui with js that tells user to try again

# only called once user is logged in
def dashboard(request):
    user_id = request.session.get('user_id')
    ring_user = RichUser.objects.get(user_id=user_id)

    groups = ring_user.group_set.all()
    if len(groups)==0:
        return render_to_response('dashboard.html',{'uncreated':True},context_instance=RequestContext(request))
    else:
        return render_to_response('dashboard.html',{'uncreated':False,'groups':groups},context_instance=RequestContext(request))

def _create_user(request):
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
    ring_user = RichUser(user=user)
    ring_user.save()

    request.session.__setitem__('logged_in', True)
    request.session.__setitem__('user_id', ring_user.user_id)
    return ring_user

def create_user(request):
    
    if 'group_code' in request.POST:
        username = request.POST['email']
        group_code = request.POST['group_code']
        try:
            rich_user = _create_user(request)
            _add_user(rich_user, group_code)
            return HttpResponseRedirect("/dashboard/")

        except:
           return HttpResponseServerError("Error processing your input. Please try again.")  

    _create_user(request)
    return HttpResponseRedirect("/dashboard/")

def create_group(request):
    if request.method != 'POST':
        return HttpResponseServerError("Bad request type: " + request.method)
    if 'group_name' not in request.POST:
        return HttpResponseServerError("No 'group_name' in POST")

    group_name = request.POST['group_name']
    user_id = request.session.get('user_id')

    user = RichUser.objects.get(user_id=user_id)
    django_group = Group(group_name=group_name)
    django_group.save()
    django_group.users.add(user)
    django_group.save()

    groups = user.group_set.all()
    return render_to_response(
        'dashboard.html',{'groups':groups},context_instance=RequestContext(request))

# shows group home page
def group(request):
    if request.method != 'GET':
        return HttpResponseServerError("Bad request type: " + request.method)
    if 'group_id' not in request.GET:
        return HttpResponseServerError("No 'group_id' in GET")

    group_id = request.GET['group_id']
    group = Group.objects.get(group_id=group_id)
    request.session.__setitem__('group_id', group_id)
    return render_to_response(
        'group-home.html',{'group':group}, context_instance=RequestContext(request))

""" Members """

def _add_user(rich_user, group_code):
    encoded_group = GroupCode.objects.get(group_code = group_code)
    group = encoded_group.group
    group.users.add(rich_user)
    
    #setting the code to "used" status
    encoded_group.used = True
    encoded_group.save()

    group.save()

def add_user_to_group(request):

    group_id = request.session.get('group_id')
    group = Group.objects.get(group_id=group_id)
    new_member_email = request.GET['new_member_email']
    try:
        django_user = User.objects.get(username=new_member_email)
        ring_user = RichUser.objects.get(user=django_user)
    except User.DoesNotExist:
        
        stringset = string.ascii_letters+string.digits
        code = ''.join([stringset[i%len(stringset)] \
                for i in [ord(x) for x in os.urandom(6)]])
        group_code = GroupCode(group_code = code, group=group, used=False)
        group_code.save()
        
        subject = "You've Been Invited to Ring!"
        content = "Please create an account at the following link: http://54.245.118.39:8000/group_signup." \
        +  "\n\n Please use the following code when signing up: " + code + "!"
        
        #TODO: change this to the actual users, obvs.
        email = EmailMessage(subject, content, to=['franklin.z.yang@gmail.com']) 
        email.send()

    return render_to_response(
        'group-members.html',{'group':group}, context_instance=RequestContext(request))

def group_members(request):
    group_id = request.session.get('group_id')
    group = Group.objects.get(group_id=group_id)
    return render_to_response(
        'group-members.html', {'group':group},context_instance=RequestContext(request))

""" Messages """
def group_messages(request):
    group_id = request.session.get('group_id')
    group = Group.objects.get(group_id=group_id)
    threads = group.messagethread_set.all()
    threads_with_snippets = []
    for thread in threads:
        for message in thread.message_set.all():
            message.snippet = message.content[:60] # first 60 characters of string
            message.save()
    return render_to_response(
        'group-messages.html', {'threads':threads},context_instance=RequestContext(request))

def send_new_message(request):
    user_id = request.session.get('user_id')
    ring_user = RichUser.objects.get(user_id=user_id)
    username = ring_user.user.username
    group_id = request.session.get('group_id')
    group = Group.objects.get(group_id=group_id)
    subject = request.GET['subject']
    content = request.GET['content']
    try:
        thread = MessageThread.objects.get(subject=subject)
    except MessageThread.DoesNotExist:
        thread = MessageThread(group=group, subject=subject)
        thread.save()
    message = Message(sent=datetime.datetime.now(), 
        content=content, thread=thread, author_id=user_id, author_name=username);
    message.save()
    #TODO: change this to the actual users, obvs.
    email = EmailMessage(subject, content, to=['franklin.z.yang@gmail.com']) 
    email.send()

    twilio_acct_sid = 'AC426a046e4f6eac58a3f733e2cc1b0f6a'
    twilio_auth_token = '1c59f69ee46da00b1a728ef43ba83ce6'
    twilioclient = TwilioRestClient(twilio_acct_sid, twilio_auth_token)
    sms = twilioclient.sms.messages.create(to='+15714816721', from_='+15714827875',body=content)
    #from_ field is our Twilio number
    # the actual sms received has "Sent from your Twilio trial account" prepended to the body 
    return HttpResponseRedirect('/messages/')

""" Bulletin Board """
def group_bulletin(request):
    group_id = request.session.get('group_id')
    group = Group.objects.get(group_id=group_id)
    pinned_items = group.pinneditem_set.all()
    data = [] # to be returned in HttpResponse
    for pinned_item in pinned_items:
        r = __embedly(pinned_item.url) # calls helper function
        dict={ 
            'url':pinned_item.url, 
            'author_name':pinned_item.author_name, 
            'creation_date':pinned_item.creation_date, 
            'caption':pinned_item.caption }
        if r.status_code==200:
            content = json.loads(r.content)
            for k,v in content.items():
                dict[k]=content[k]

        data.append(dict)
    return render_to_response(
        'group-bulletin.html', {'embedly_items':data},context_instance=RequestContext(request))
   
# private helper that uses Embed.ly API to pull images and synopsis from links, similar to Facebook
# uh...there's an embedly-python repo on Github, may refactor later <_<
def __embedly(url):
    data = {
        'url':urllib.quote(url), # escapes special characters
        'words':20, # number of words that will be returned in the description (default 50)
        'key':'1bf66f45eaea446a9514e4cd1d8ce4eb' # Embed.ly key
    }
    query = '&'.join(['%s=%s' % (k,v) for k,v in data.items()])
    fetch_url = 'http://api.embed.ly/1/oembed?%s' % query
    r = requests.get(fetch_url) # uses the requests lib
    return r

def pin_new_item(request):
    user_id = request.session.get('user_id')
    ring_user = RichUser.objects.get(user_id=user_id)
    username = ring_user.user.username
    group_id = request.session.get('group_id')
    group = Group.objects.get(group_id=group_id)
    url = request.GET['url']
    caption = request.GET['caption'] 
    pinned_item = PinnedItem(
        url=url, group=group, author_id=user_id, author_name=username, caption=caption); 
    pinned_item.save()
    return HttpResponseRedirect('/bulletin/')

""" Documents """
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
