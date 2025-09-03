from django.db import models
from django.contrib.auth.models import AbstractUser
from employees.models import Employee

# Create your models here.


class User(AbstractUser):
    username = models.CharField(max_length=100 , unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(blank=True , unique=True)
    USERNAME_FIELD = 'username'
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=64, blank=True, null=True)
    is_employee = models.BooleanField(default=False)
    REQUIRED_FIELDS=[]
    def __str__(self) -> str:
        return self.username
    
class Employee_User(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    employee = models.OneToOneField(Employee , on_delete=models.CASCADE)