# Create your views here.
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404, HttpResponseServerError, HttpResponseRedirect
from django.contrib.auth.models import User

import datetime, simplejson

def index(request):
    return render_to_response('index.html')
    
