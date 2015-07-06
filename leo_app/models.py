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


class Vehicle(models.Model):
    registration = models.CharField(unique=True, max_length=10)
    make = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    engine_capacity = models.DecimalField(decimal_places=1, max_digits=2)
    owner = models.ForeignKey(UserProfile, blank=True, null=True)


class InfrastructureType(models.Model):
    code = models.IntegerField(unique=True)
    short_description = models.CharField(max_length=50)


class Infrastructure(models.Model):
    infrastructure_type = models.ForeignKey(InfrastructureType)
    longitude = models.DecimalField(decimal_places=4, max_digits=7)
    latitude = models.DecimalField(decimal_places=4, max_digits=6)
    # TODO: Need to add CompanyProfile model aswell, will use here as owner of infrastructure
    owner = models.ForeignKey(UserProfile)


class Sighting(models.Model):
    sighting_datetime = models.DateTimeField()
    year_month_slug = models.CharField(max_length=20)
    vehicle = models.ForeignKey(Vehicle, blank=True, null=True)
    human = models.ForeignKey(UserProfile, blank=True, null=True)
    infrastructure = models.ForeignKey(Infrastructure, blank=True, null=True)
    infridgement = models.ForeignKey(Infridgement)
    longitude = models.DecimalField(decimal_places=4, max_digits=7)
    latitude = models.DecimalField(decimal_places=4, max_digits=6)
 
    def save(self, *args, **kwargs):
        if not self.vehicle and not self.human and not self.infrastructure:
            raise TypeError('Atleast one of vehicle, human or infrastructure must be populated when submitting a sighting')
        self.year_month_slug = self.sighting_datetime.strftime('%b/%Y')
        super(Sighting, self).save(*args, **kwargs)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])