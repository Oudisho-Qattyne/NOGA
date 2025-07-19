from django.shortcuts import render
from rest_framework.views import APIView , Response , status
from rest_framework import generics 
from .models import *
from .serializers import *
from django.db.models.deletion import ProtectedError


# Create your views here.

class DiscountsAPIView(generics.ListAPIView , generics.CreateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer


class DiscountAPIView(generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.has_products:
                products = Discount_Product.objects.filter(discount=instance)
                for product in products:
                    if product.has_options:
                        Discount_Product_Option.objects.filter(discount_product=product).delete()
                    product.delete()
            if instance.has_categories:
                categories = Discount_Category.objects.filter(discount = instance)
                for category in categories:
                    if category.has_options:
                        Discount_Category_Option.objects.filter(discount_category=category).delete()
                    category.delete()
            super().delete(request, *args, **kwargs)
            return Response({"message": "Discount deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Response({"message": "Discount can't be deleted"}, status=status.HTTP_400_BAD_REQUEST)
        

class DiscountsAPIView(generics.ListAPIView , generics.CreateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer


class DiscountAPIView(generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.has_products:
                products = Discount_Product.objects.filter(discount=instance)
                for product in products:
                    if product.has_options:
                        Discount_Product_Option.objects.filter(discount_product=product).delete()
                    product.delete()
            if instance.has_categories:
                categories = Discount_Category.objects.filter(discount = instance)
                for category in categories:
                    if category.has_options:
                        Discount_Category_Option.objects.filter(discount_category=category).delete()
                    category.delete()
            super().delete(request, *args, **kwargs)
            return Response({"message": "Discount deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Response({"message": "Discount can't be deleted"}, status=status.HTTP_400_BAD_REQUEST)
        

class OffersAPIView(generics.ListAPIView , generics.CreateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer


class OfferAPIView(generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            products = Offer_Product.objects.filter(offer=instance)
            for product in products:
                if product.has_options:
                    Offer_Product_Option.objects.filter(offer_product=product).delete()
                product.delete()
            
            super().delete(request, *args, **kwargs)
            return Response({"message": "Offer deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Response({"message": "Offer can't be deleted"}, status=status.HTTP_400_BAD_REQUEST)
        
class CouponsAPIView(generics.CreateAPIView , generics.ListAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

class CouponAPIView(generics.UpdateAPIView , generics.DestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

class PurchasesAPIView(generics.CreateAPIView , generics.ListAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

class PurchaseAPIView(generics.UpdateAPIView , generics.DestroyAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.status == "pending":
                products = Purchased_Products.objects.filter(purchase=instance)
                for product in products:
                    branch = instance.branch          
                    branch_product = Branch_Products.objects.filter(product=product.product , branch=branch).first()
                    branch_product.quantity += product.quantity
                    branch_product.save()
                    product.delete()
                super().delete(request, *args, **kwargs)
                return Response({"message": "purchase deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            return Response({"message": "purchase can't be deleted"}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Response({"message": "purchase can't be deleted"}, status=status.HTTP_400_BAD_REQUEST)

class CustomersAPIVIew(generics.CreateAPIView , generics.ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class CustomerAPIVIew(generics.UpdateAPIView , generics.DestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer