from django.db import models
from products.models import Product , Option , Category , Variant
from branches.models import Branch
from django.core.exceptions import ValidationError
# Create your models here.

class Customer(models.Model):
    national_number = models.CharField(max_length=200 , unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    gender = models.BooleanField(default=True)

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


# class Offer(models.Model):
#     start_date = models.DateField()
#     end_date = models.DateField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     price = models.FloatField()
#     @property
#     def offer_products(self):
#         return self.offer_product_set.all()
    
# class Offer_Product(models.Model):
#     offer = models.ForeignKey(Offer , on_delete=models.PROTECT)
#     product = models.ForeignKey(Product , on_delete = models.PROTECT)
#     has_options = models.BooleanField()
#     options = models.ManyToManyField(Option , through="Offer_Product_Option")
#     quantity = models.PositiveBigIntegerField()

# class Offer_Product_Option(models.Model):
#     offer_product = models.ForeignKey(Offer_Product , on_delete=models.PROTECT)
#     option = models.ForeignKey(Option , on_delete=models.PROTECT)


class Coupon(models.Model):
    DISOUCT_TYPES = [
        ("fixed" , "fixed"),
        ("percentage" , "percentage")
    ]
    code = models.CharField(max_length=200 , null=False , unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()
    discount_type = models.CharField(max_length=30 , choices=DISOUCT_TYPES)
    min_price = models.FloatField(null=True)
    max_price = models.FloatField(null=True)
    quantity = models.PositiveIntegerField()

class Purchase(models.Model):
    PURCHASE_STATUES = [
        ('pending', 'pending'),
        ('processing', 'processing'),
        ('completed', 'completed'),
        ('cancelled', 'cancelled')
    ]
    branch = models.ForeignKey(Branch , on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer , on_delete=models.PROTECT)
    status = models.CharField(max_length=100 , choices=PURCHASE_STATUES , default="pending")
    date_of_purchase = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    subtotal_price = models.FloatField(default=0)
    total_price = models.FloatField(default=0)
    has_coupon = models.BooleanField(default=False)
    coupon = models.ForeignKey(Coupon , on_delete = models.PROTECT , null=True)
    # has_offers = models.BooleanField(default=False)
    # purchased_offers = models.ManyToManyField(Offer)
    @property
    def purchased_products(self):
            return self.purchased_products_set.all()
    
class Purchased_Products(models.Model):
    purchase = models.ForeignKey(Purchase , on_delete=models.CASCADE)
    product = models.ForeignKey(Variant , on_delete=models.CASCADE)
    wholesale_price = models.FloatField()
    selling_price = models.FloatField()
    total_price = models.FloatField()
    has_discount = models.BooleanField(default=False)
    discount = models.ForeignKey(Discount , on_delete=models.CASCADE , null=True)
    quantity = models.PositiveIntegerField(default=1)

    def clean(self):
        if self.quantity<=0:
            raise ValidationError("quantity must be more than 0")
        if self.selling_price<=0:
            raise ValidationError("selling_price must be more than 0")
        if self.total_price<=0:
            raise ValidationError("total_price must be more than 0")
        
    def save(self,*args,**kwargs):
        self.clean()
        return super().save(*args,**kwargs)
    class Meta:
        unique_together=['purchase','product']

