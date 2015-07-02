from django.db import models
from django.contrib.auth.models import User
import hashlib


class Ribbit(models.Model):
    content = models.CharField(max_length=140)
    user = models.ForeignKey(User)
    creation_date = models.DateTimeField(auto_now=True, blank=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    mobile = models.CharField(max_length=7)
    #follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False)

    def gravatar_url(self):
        return "http://www.gravatar.com/avatar/%s?s=50" % hashlib.md5(self.user.email).hexdigest()


class Infridgement(models.Model):
    code = models.IntegerField(unique=True)
    short_description = models.CharField(max_length=50)

class Sighting(models.Model):
    pass

class Vehicle(models.Model):
    registration = models.CharField(unique=True, max_length=10)
    make = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    engine_capacity = models.DecimalField(decimal_places=1, max_digits=2)
    owner = models.ForeignKey(UserProfile, blank=True, null=True)
 
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])