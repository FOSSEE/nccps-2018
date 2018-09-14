from django.db import models
from django.contrib.auth.models import User

from social.apps.django_app.default.models import UserSocialAuth
from nccps2018 import settings
from django.core.validators import RegexValidator
import os

position_choices = (
    ("student", "Student"),
    ("faculty", "Faculty"),
    ("industry_people", "Industry People"),
)

source = (
    ("FOSSEE website", "FOSSEE website"),
    ("Google", "Google"),
    ("Social Media", "Social Media"),
    ("From other College", "From other College"),
)

title = (
    ("Mr", "Mr."),
    ("Miss", "Ms."),
    ("Professor", "Prof."),
    ("Doctor", "Dr."),
)


def get_document_dir(instance, filename):
    # ename, eext = instance.user.email.split("@")
    fname, fext = os.path.splitext(filename)
    # print "----------------->",instance.user
    return '%s/attachment/%s/%s.%s' % (instance.user, instance.proposal_type, fname+'_'+str(instance.user), fext)


class Proposal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    name_of_authors = models.CharField(max_length=200, default='None')
    about_the_authors = models.TextField(max_length=500)
    email = models.CharField(max_length=128)
    phone = models.CharField(max_length=20)
    title = models.CharField(max_length=250)
    abstract = models.TextField(max_length=10, default='abstract')
    prerequisite = models.CharField(max_length=750)
    duration = models.CharField(max_length=100)
    attachment = models.FileField(upload_to=get_document_dir)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=100, default='Pending', editable=True)
    proposal_type = models.CharField(max_length=100)
    tags = models.CharField(max_length=250)
    open_to_share = models.CharField(max_length=2, default=1)


class Ratings(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE,)
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    rating = models.CharField(max_length=700)


class Comments(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE,)
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    comment = models.CharField(max_length=700)
    # rate = models.CharField(max_length =100)

# profile module


class Profile(models.Model):
    """Profile for users"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=32, blank=True, choices=title)
    institute = models.CharField(max_length=150)
    phone_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(
                    regex=r'^.{10}$', message=(
                        "Phone number must be entered \
                                in the format: '9999999999'.\
                                Up to 10 digits allowed.")
                    )], null=False)
    position = models.CharField(max_length=32, choices=position_choices,
                                default='student',
                                help_text='Selected catagoery ID shold be required')
    how_did_you_hear_about_us = models.CharField(
        max_length=255, blank=True, choices=source)
    is_email_verified = models.BooleanField(default=False)
    activation_key = models.CharField(max_length=255, blank=True, null=True)
    key_expiry_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return u"id: {0}| {1} {2} | {3} ".format(
            self.user.id,
            self.user.first_name,
            self.user.last_name,
            self.user.email
        )