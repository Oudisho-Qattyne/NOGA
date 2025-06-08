from django.db import models



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
    Attribute = models.ForeignKey(Attribute , on_delete=models.PROTECT)

class Option(models.Model):
    option = models.CharField(max_length=50)
    attribute = models.ForeignKey(Attribute , on_delete=models.PROTECT)


    
class Option_Unit(models.Model):
    option = models.OneToOneField(Option , on_delete=models.CASCADE)
    unit = models.OneToOneField(Unit ,  on_delete=models.CASCADE)

class Category(models.Model):
    category = models.CharField(max_length=100 , unique=True)
    parent_category = models.ForeignKey("Category" , on_delete=models.CASCADE , related_name='subcategories' , null=True)
    attributes = models.ManyToManyField(Attribute , through='Category_Attribute')
    def __str__(self) -> str:
        return self.category
    
class Category_Attribute(models.Model):
    category = models.ForeignKey(Category , on_delete=models.PROTECT)
    Attribute = models.ForeignKey(Attribute , on_delete=models.PROTECT)



class Product(models.Model):
    product_name = models.CharField(max_length=100 , unique=True)
    category = models.ForeignKey(Category , on_delete=models.PROTECT)
    qr_code = models.CharField(max_length=300 , null=True , blank=True)
    qr_codes_download = models.CharField(max_length=300 , null=True , blank=True)
    def __str__(self) -> str:
        return self.product_name
    
class Variant(models.Model):
    product = models.ForeignKey(Product , on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    wholesale_price = models.FloatField()
    selling_price = models.FloatField()
    options = models.ManyToManyField(Option , through='Variant_Option')

class Variant_Option(models.Model):
    variant = models.ForeignKey(Variant , on_delete=models.PROTECT)
    option = models.ForeignKey(Option , on_delete=models.PROTECT)


    

