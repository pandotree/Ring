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

class MessageThread(models.Model):
    group = models.ForeignKey(Groups)
    subject = models.TextField() #Not sure if we should limit subject line with CharField

class Message(models.Model):
    sent = models.DateTimeField()
    #subject = models.TextField() #Not sure if we should limit subject line with CharField
    content = models.TextField()
    author_id = models.IntegerField()
    author_name = models.CharField(max_length=64)
    thread = models.ForeignKey(MessageThread)

class PinnedItem(models.Model):
    creation_date = models.DateTimeField(auto_now=True)
    url = models.CharField(max_length=300) # is there a better way of representing this?
    group = models.ForeignKey(Groups)
    author_id = models.IntegerField()
    author_name = models.CharField(max_length=64)
    caption = models.TextField()

#TODO VALIDATION
