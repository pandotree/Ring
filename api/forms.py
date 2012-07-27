from django import forms
from django.db import models
from django.forms import ModelForm
from registration.forms import RegistrationForm
from . import models #does this work?

class GroupForm(ModelForm):
	class Meta:
		model = models.Groups

class Users(ModelForm):
	class Meta:
		model = models.Users
		fields = ('user_id', 'email_address', 'phone_number', 'password')