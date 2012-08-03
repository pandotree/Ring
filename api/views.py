# Create your views here.
from .models import Users
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.http import HttpResponse, Http404, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext
''''''
import datetime
import json as simplejson

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
        request.session.__setitem__('logged_in', True)
        return HttpResponseRedirect("/dashboard/")

    return render_to_response('index.html',context_instance=RequestContext(request)) #eventually update ui with js that tells user to try again


def dashboard(request):
    logged_in = request.session.get('logged_in', False)
    if(not logged_in):
        return HttpResponse("Please log in!") #find a partial that we can render, or maybe redirect to homepage
    return render_to_response('dashboard.html',context_instance=RequestContext(request))
    
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