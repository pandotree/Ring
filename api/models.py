from django.db import models
from django.contrib.auth.models import User

#Create models here

class Users(models.Model):
	user = models.OneToOneField(User)
	university = models.CharField(max_length=32)

class Groups(models.Model):
	group_name = models.CharField(max_length=64)
	group_id = models.AutoField(primary_key=True)
	created = models.DateField()
	user_id = models.ManyToManyField(User, related_name="user_set")


#TODO VALIDATION
