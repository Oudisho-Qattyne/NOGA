from django.db import models
# Create your models here.

class City(models.Model):
    def __str__(self) -> str:
        return self.city_name
    city_name = models.CharField(max_length=100 , unique=True)
    
class Branch(models.Model):
    number = models.IntegerField()
    location = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    manager = models.OneToOneField("employees.Employee", on_delete=models.PROTECT , related_name='manager_of_branch')
    city = models.ForeignKey(City , on_delete=models.PROTECT )
    
class Branch_Products(models.Model):
    branch = models.ForeignKey(Branch , on_delete=models.PROTECT)
    product = models.ForeignKey("products.Variant" , on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    