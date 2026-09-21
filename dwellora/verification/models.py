from django.db import models
from accounts.models import Profile
from services.models import Service

class AccountVerification(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)




# Create your models here.
