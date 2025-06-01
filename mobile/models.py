from django.db import models
from NOGA.utils import *
from users.models import User
# Create your models here.

class Client_Profile(models.Model):
    national_number=models.IntegerField(unique=True)
    first_name=models.CharField(max_length=100)
    middle_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    email=models.EmailField(max_length=50 , default="test@gmail.com")
    birth_date=models.DateField()
    gender=models.BooleanField()
    address=models.CharField(max_length=50)
    phone=models.CharField(max_length=100)
    image = models.ImageField(upload_to=upload_to, blank=True, null=True , validators=[validate_image_size])
    user = models.OneToOneField(User , on_delete=models.PROTECT)
    