from django.db import models
from NOGA.utils import *
from users.models import User
from products.models import Product
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
    
class Comment(models.Model):
    user_id=models.ForeignKey(User,on_delete=models.PROTECT)
    product_id=models.ForeignKey(Product,on_delete=models.PROTECT)
    comment_text=models.CharField(max_length=300)
    replay_to=models.ForeignKey("Comment",on_delete=models.PROTECT,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


class Like(models.Model):
    user_id=models.ForeignKey(User,on_delete=models.PROTECT)
    product_id=models.ForeignKey(Product,on_delete=models.PROTECT)


class Save(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    saves_at=models.DateTimeField(auto_now=True)

    class Meta:
        unique_together=[('user','product')]
    
    def __str__(self):
        return f"{self.user} saved {self.product} at {self.saves_at}"
    

class Review(models.Model):
    RATING_CHOICES=[
        (1,'⭐'),(2,'⭐⭐'),(3,'⭐⭐⭐'),(4,'⭐⭐⭐⭐') ,(5,'⭐⭐⭐⭐⭐')   
    ]
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='reviews')
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='reviews')
    rating=models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment=models.TextField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        unique_together=[('user','product')]
        ordering=['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"