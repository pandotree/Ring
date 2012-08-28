# Create your views here.

from .models import Users, Groups, MessageThread, Message, PinnedItem
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
            ring_user = Users.objects.get(user=user)
        except Users.DoesNotExist: # sanity check, this should never happen under normal use cases. potentially refactor to get_object_or_404 and catch the http404 exception
            return HttpResponse("Oops, looks like you haven't created an account with us yet!") 
        request.session.__setitem__('logged_in', True)
        request.session.__setitem__('user_id', ring_user.user_id)
        return HttpResponseRedirect('/dashboard/')
    else:
        return HttpResponse('Your username and password were incorrect') #eventually update ui with js that tells user to try again

# only called once user is logged in
def dashboard(request):
    user_id = request.session.get('user_id')
    ring_user = Users.objects.get(user_id=user_id)

    groups = ring_user.user_set.all()
    if len(groups)==0:
        return render_to_response('dashboard.html',{'uncreated':True},context_instance=RequestContext(request))
    else:
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
    ring_user = Users(user=user, university="UPenn", phone_number=1112223333, preferred_contact_method=1)
    ring_user.save()

    return HttpResponseRedirect("/dashboard/")

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
    django_group.save()

    groups = user.user_set.all()
    return render_to_response('dashboard.html',{'groups':groups},context_instance=RequestContext(request))

# shows group home page
def group(request):
    if request.method != 'GET':
        return HttpResponseServerError("Bad request type: " + request.method)
    if 'group_id' not in request.GET:
        return HttpResponseServerError("No 'group_id' in GET")

    group_id = request.GET['group_id']
    group = Groups.objects.get(group_id=group_id)
    request.session.__setitem__('group_id', group_id)
    return render_to_response('group-home.html',{'group':group}, context_instance=RequestContext(request))

""" Members """
def add_user_to_group(request):
    group_id = request.session.get('group_id')
    group = Groups.objects.get(group_id=group_id)
    new_member_email = request.GET['new_member_email']
    try:
        django_user = User.objects.get(username=new_member_email)
        ring_user = Users.objects.get(user=django_user)
    except User.DoesNotExist:
        django_user = User.objects.create_user(new_member_email, new_member_email, "temp"); #TODO: send an email to the user telling them about their new account and temp password
        ring_user = Users(user=django_user, university="UPenn", phone_number=1112223333, preferred_contact_method=1)
        ring_user.save()
    group.users.add(ring_user)
    group.save()
    return render_to_response('group-members.html',{'group':group}, context_instance=RequestContext(request))

def group_members(request):
    group_id = request.session.get('group_id')
    group = Groups.objects.get(group_id=group_id)
    return render_to_response('group-members.html', {'group':group},context_instance=RequestContext(request))

""" Messages """
def group_messages(request):
    group_id = request.session.get('group_id')
    group = Groups.objects.get(group_id=group_id)
    threads = group.messagethread_set.all()
    all_threads = []
    for thread in threads:
        all_threads.append((thread.subject, thread.message_set.all()))
    return render_to_response('group-messages.html', {'threads':threads},context_instance=RequestContext(request))

def send_new_message(request):
    user_id = request.session.get('user_id')
    ring_user = Users.objects.get(user_id=user_id)
    username = ring_user.user.username
    group_id = request.session.get('group_id')
    group = Groups.objects.get(group_id=group_id)
    subject = request.GET['subject']
    content = request.GET['content']
    try:
        thread = MessageThread.objects.get(subject=subject)
    except MessageThread.DoesNotExist:
        thread = MessageThread(group=group, subject=subject)
        thread.save()
    message = Message(sent=datetime.datetime.now(), content=content, thread=thread, author_id=user_id, author_name=username);
    message.save()
    email = EmailMessage(subject, content, to=['gracewang92@gmail.com']) #TODO: change this to the actual users, obvs.
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
    group = Groups.objects.get(group_id=group_id)
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
            if 'title' in content:
                dict['title']=content['title']
            if 'provider_name' in content:
                dict['provider_name']=content['provider_name']
            if 'provider_url' in content:
                dict['provider_url']=content['provider_url']
            if 'description' in content:
                dict['description']=content['description']
            if 'thumbnail_url' in content:
                dict['thumbnail_url']=content['thumbnail_url']
            if 'type' in content and content['type']=='video':
                dict['video']=content['html']

        data.append(dict)
    return render_to_response('group-bulletin.html', {'embedly_items':data},context_instance=RequestContext(request))
   
# private helper that uses the Embed.ly API to pull images and synopsis from links, similar to Facebook
# uh...so I did all this work and then found out there's an embedly-python repo on Github, may refactor later <_<
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
    ring_user = Users.objects.get(user_id=user_id)
    username = ring_user.user.username
    group_id = request.session.get('group_id')
    group = Groups.objects.get(group_id=group_id)
    url = request.GET['url']
    caption = request.GET['caption'] 
    pinned_item = PinnedItem(url=url, group=group, author_id=user_id, author_name=username, caption=caption); 
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
