from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


class Status(models.Model):
    """Picture to User proxy model storing the current status of watching"""
    episode = models.SmallIntegerField(validators=[MinValueValidator(1)], default=1)
    season = models.SmallIntegerField(validators=[MinValueValidator(1)], default=1)
    picture = models.ForeignKey(to='Picture', on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    finished = models.BooleanField(default=False)


class Picture(models.Model):
    """Model to store picture-related info"""
    FILM = "F"
    SERIES = "S"
    PICTURE_TYPE_CHOICES = (
        (FILM, "Film"),
        (SERIES, "Series"),
    )
    name = models.CharField(max_length=256)
    user = models.ManyToManyField(User, through=Status)
    type = models.CharField(
        max_length=1,
        choices=PICTURE_TYPE_CHOICES,
        default=FILM,
    )


class Link(models.Model):
    """Model to store link for series"""
    source = models.URLField()
    season = models.SmallIntegerField(validators=[MinValueValidator(1)], default=1)
    episode = models.SmallIntegerField(validators=[MinValueValidator(1)], default=1)
    picture = models.ForeignKey(to=Picture, on_delete=models.CASCADE)
