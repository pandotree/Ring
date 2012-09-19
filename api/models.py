from django.db import models
from django.contrib.localflavor.us.forms import USPhoneNumberField
from django.contrib.auth.models import User

class RichUser(models.Model):
    user                      = models.OneToOneField(User)
    university                = models.CharField(max_length=32, null=True)
    phone_number              = models.IntegerField(null=True)
    EMAIL                     = 1
    SMS                       = 2
    EMAILANDSMS               = 3
    PREFERRED_CONTACT_CHOICES = (
        (EMAIL, 'Email only'),
        (SMS, 'SMS only'),
        (EMAILANDSMS, 'Email and SMS'),
    )
    preferred_contact_method  = models.IntegerField(choices=PREFERRED_CONTACT_CHOICES, default=EMAIL)

class Group(models.Model):
	group_name = models.CharField(max_length=64)
	group_id   = models.AutoField(primary_key=True)
	created    = models.DateTimeField(auto_now=True)
	users      = models.ManyToManyField(RichUser, related_name="group_set")

class GroupCode(models.Model):
    group_code = models.CharField(max_length=10)
    group   = models.ForeignKey(Group)
    used       = models.BooleanField() 

class MessageThread(models.Model):
    group   = models.ForeignKey(Group)
    subject = models.TextField() #Not sure if we should limit subject line with CharField

class Message(models.Model):
    sent        = models.DateTimeField()
    content     = models.TextField()
    snippet     = models.TextField(null=True) #only filled in later, before sending messages to view
    author_id   = models.IntegerField()
    author_name = models.CharField(max_length=64)
    thread      = models.ForeignKey(MessageThread)

class PinnedItem(models.Model):
    creation_date = models.DateTimeField(auto_now=True)
    url           = models.CharField(max_length=300) # is there a better way of representing this?
    group         = models.ForeignKey(Group)
    author_id     = models.IntegerField()
    author_name   = models.CharField(max_length=64)
    caption       = models.TextField()

#TODO VALIDATION
