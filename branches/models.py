from django.utils.timezone import now
from django.db import models
# Create your models here.
class City(models.Model):
    def __str__(self) -> str:
        return self.city_name
    city_name = models.CharField(max_length=100 , unique=True)
    
class Branch(models.Model):
    def __str__(self) -> str:
        return self.city.city_name + str(self.number)
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
    
class Camera(models.Model):
    CAMERA_TYPES=[
        ('monitoring', 'Monitoring'),
        ('attendance', 'Attendance'),
        ('visitors', 'Visitors'),
    ]
    camera_type = models.CharField(max_length=30 , default="monitoring")
    branch = models.ForeignKey(Branch , on_delete=models.PROTECT)
    source_url = models.CharField(max_length=300)
    view_url = models.CharField(max_length=300)
    is_active = models.BooleanField(default=False)
    area_points = models.JSONField(null=True, blank=True)

class Branch_Visitors(models.Model):
    branch = models.ForeignKey(Branch , on_delete=models.CASCADE)
    date = models.DateField(default=now)
    visitors_count = models.IntegerField(default=0)