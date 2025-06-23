from django.db import models
from products.models import Product , Option , Category

# Create your models here.
class Discount(models.Model):
    DISOUCT_TYPES = [
        ("fixed" , "fixed"),
        ("percentage" , "percentage")
    ]
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()
    discount_type = models.CharField(max_length=30 , choices=DISOUCT_TYPES)
    has_products = models.BooleanField()
    has_categories = models.BooleanField()
    for_every_product = models.BooleanField(default=False)
    for_every_product_exept = models.BooleanField(default=False)
    @property
    def discount_products(self):
        return self.discount_product_set.all()
    @property
    def discount_categories(self):
        return self.discount_category_set.all()
    
class Discount_Product(models.Model):
    discount = models.ForeignKey(Discount , on_delete=models.PROTECT)
    product = models.ForeignKey(Product , on_delete = models.PROTECT)
    has_options = models.BooleanField()
    options = models.ManyToManyField(Option , through="Discount_Product_Option")

class Discount_Product_Option(models.Model):
    discount_product = models.ForeignKey(Discount_Product , on_delete=models.PROTECT)
    option = models.ForeignKey(Option , on_delete=models.PROTECT)

class Discount_Category(models.Model):
    discount = models.ForeignKey(Discount , on_delete=models.PROTECT)
    category = models.ForeignKey(Category , on_delete=models.PROTECT)
    has_options = models.BooleanField()
    options = models.ManyToManyField(Option , through="Discount_Category_Option")


class Discount_Category_Option(models.Model):
    discount_category = models.ForeignKey(Discount_Category , on_delete=models.PROTECT)
    option = models.ForeignKey(Option , on_delete=models.PROTECT)
