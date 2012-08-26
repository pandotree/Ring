from django.db import models
from django.contrib.localflavor.us.forms import USPhoneNumberField
from django.contrib.auth.models import User

#Create models here TODO: rename to singular

class Users(models.Model):
	user = models.OneToOneField(User)
	university = models.CharField(max_length=32)
	# phone_number = USPhoneNuberField() #
	phone_number = models.IntegerField()
	# 1: email, #2: phone, #3: both. TODO: switch to enum?
	preferred_contact_method = models.IntegerField() #
    
class Groups(models.Model):
	group_name = models.CharField(max_length=64)
	group_id = models.AutoField(primary_key=True)
	created = models.DateTimeField(auto_now=True)
	users = models.ManyToManyField(Users, related_name="user_set") #TODO: rename to groups_set

class Messages(models.Model):
	sent = models.DateTimeField()
	subject = models.TextField() #Not sure if we should limit subject line with CharField
	content = models.TextField()
	group = models.ForeignKey(Groups)

#TODO VALIDATION
