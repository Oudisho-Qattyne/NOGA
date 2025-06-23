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