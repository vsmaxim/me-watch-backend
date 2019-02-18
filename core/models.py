from django.contrib.auth.models import User
from django.db import models


class SocialInformation(models.Model):
    """Model to store information about social accounts like vk.com, shikimori.org etc"""
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    social_type = models.CharField(max_length=256)
    social_user_id = models.CharField(max_length=256)
