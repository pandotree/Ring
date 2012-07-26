from django.db import models
from django.contrib.auth.models import User

#Create models here

class Users(models.Model):
	user = models.OneToOneField(User)
	university = models.CharField(max_length=32)
  phone_number = us.models.PhoneNumberField()

class Groups(models.Model):
	group_name = models.CharField(max_length=64)
	group_id = models.AutoField(primary_key=True)
	created = models.DateTimeField()
	user_id = models.ManyToManyField(User, related_name="user_set")

class Messages(models.Model):
  sent = models.DateTimeField()
  subject = models.TextField() #Not sure if we should limit subject line with CharField
  content = models.TextField()

#TODO VALIDATION
