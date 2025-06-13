from django.db import models
from branches.models import Branch
from NOGA.utils import *

# Create your models here.
class Unit(models.Model):
    unit = models.CharField(max_length=50 , unique=True)
    def __str__(self) -> str:
        return self.unit
    

class Attribute(models.Model):
    ATTRIBUTE_TYPES = [
        ('number','number'),
        ('string','string')
    ]
    attribute = models.CharField(max_length=50)
    attribute_type = models.CharField(max_length=30 , choices=ATTRIBUTE_TYPES)
    is_multivalue = models.BooleanField(default=False)
    is_categorical = models.BooleanField(default=False)
    has_unit = models.BooleanField(default=False)
    units = models.ManyToManyField(Unit , through='Attribute_Unit')

class Attribute_Unit(models.Model):
    unit = models.ForeignKey(Unit , on_delete=models.PROTECT)
    attribute = models.ForeignKey(Attribute , on_delete=models.PROTECT)

class Option(models.Model):
    option = models.CharField(max_length=50)
    attribute = models.ForeignKey(Attribute , on_delete=models.PROTECT)


    
class Option_Unit(models.Model):
    option = models.ForeignKey(Option , on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit ,  on_delete=models.CASCADE)

class Category(models.Model):
    category = models.CharField(max_length=100 , unique=True)
    parent_category = models.ForeignKey("Category" , on_delete=models.CASCADE , related_name='subcategories' , null=True)
    attributes = models.ManyToManyField(Attribute , through='Category_Attribute')
    def __str__(self) -> str:
        return self.category
    
class Category_Attribute(models.Model):
    category = models.ForeignKey(Category , on_delete=models.PROTECT)
    attribute = models.ForeignKey(Attribute , on_delete=models.PROTECT)



class Product(models.Model):
    product_name = models.CharField(max_length=100 , unique=True)
    category = models.ForeignKey(Category , on_delete=models.PROTECT)
    qr_code = models.CharField(max_length=300 , null=True , blank=True)
    qr_codes_download = models.CharField(max_length=300 , null=True , blank=True)
    linked_products = models.ManyToManyField("Product")
    def __str__(self) -> str:
        return self.product_name
    
class Linked_products(models.Model):
    product = models.ForeignKey(Product , on_delete=models.CASCADE , related_name="product1")
    linked_to = models.ForeignKey(Product , on_delete=models.CASCADE , related_name="linked_to_products")

class Variant(models.Model):
    product = models.ForeignKey(Product , on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    wholesale_price = models.FloatField()
    selling_price = models.FloatField()
    options = models.ManyToManyField(Option , through='Variant_Option')

class Variant_Option(models.Model):
    variant = models.ForeignKey(Variant , on_delete=models.PROTECT)
    option = models.ForeignKey(Option , on_delete=models.CASCADE)
    

class Transportation(models.Model):
    TRANSPORT_STATUS_TYPES=[
        ('packaging:','packaging:'),
        ('transporting','transporting'),
        ('delivered','delivered'),
        ('confirmed','confirmed'),
    ]
    transportation_status = models.CharField(max_length=30 , choices=TRANSPORT_STATUS_TYPES , default='packaging')
    source = models.ForeignKey(Branch , on_delete=models.CASCADE , null=True , related_name="from_branch")
    destination = models.ForeignKey(Branch , on_delete=models.CASCADE , null=True  , related_name="to_branch")
    code = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def transported_products(self):
        return self.transported_products_set.all()
    @property
    def received_products(self):
        return self.received_products_set.all()
    
    # transported_products = models.ManyToManyField(Variant,through="Transported_Products" )
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_code()
        super(Transportation, self).save(*args, **kwargs)


class Transported_Products(models.Model):
    transportation = models.ForeignKey(Transportation , on_delete=models.PROTECT)
    product = models.ForeignKey(Variant , on_delete=models.PROTECT , null=False)
    quantity = models.PositiveIntegerField()

class Received_Products(models.Model):
    transportation = models.ForeignKey(Transportation , on_delete=models.PROTECT)
    product = models.ForeignKey(Variant , on_delete=models.PROTECT , null=False)
    quantity = models.PositiveIntegerField()

class Transport_Request(models.Model):
    REQUEST_STATUS_TYPES=[
        ('fully-approved','fully-approved'),
        ('partially-approved','partially-approved'),
        ('waiting','waiting'),
        ('rejected','rejected'),
    ]
    request_status = models.CharField(max_length=30 , choices=REQUEST_STATUS_TYPES , default='waiting')
    branch = models.ForeignKey(Branch , on_delete=models.PROTECT)
    transportation = models.ForeignKey(Transportation , on_delete=models.PROTECT , null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def requested_products(self):
        return self.requested_products_set.all()
    
class Requested_Products(models.Model):
    PRODUCT_REQUEST_STATUS_TYPES=[
        ('fully-approved','fully-approved'),
        ('partially-approved','partially-approved'),
        ('waiting','waiting'),
        ('rejected','rejected'),
    ]
    request = models.ForeignKey(Transport_Request , on_delete=models.PROTECT)
    product_request_status = models.CharField(max_length=30 , choices=PRODUCT_REQUEST_STATUS_TYPES , default='waiting')
    product = models.ForeignKey(Variant , on_delete=models.PROTECT , null=False)
    quantity = models.PositiveIntegerField(default=0)
