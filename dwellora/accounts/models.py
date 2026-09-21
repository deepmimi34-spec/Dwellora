from django.contrib.auth.models import AbstractUser
from django.db import models


class Profile(AbstractUser):

    bio = models.CharField(max_length=100)


    class Meta:
        db_table = 'profile'
        verbose_name = 'Profile'

    def __str__(self):
        return f'{self.username} Profile'








# Create your models here.
