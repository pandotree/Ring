# Create your views here.
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext
from django.http import HttpResponse, Http404, HttpResponseServerError, HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.context_processors import csrf

import datetime, simplejson

def index(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('index.html',context_instance=RequestContext(request))
    #return render_to_response('index.html',c)

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
    """FIX LATER!!"""
    if not pw is confirm_pw:
        return HttpResponseServerError("password does not match")

    django_user = User(username=email,password=password)
    ring_user = Users(user=django_user)

    response_json = simplejson.dumps({'email':email})
    #return HttpResponse(response_json, content_type="application/json")
    return render_to_response('success.html',context_instance=RequestContext(request))
    #return render_to_response('success.html',c)
