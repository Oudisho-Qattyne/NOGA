from django.shortcuts import render
from .models import *
from rest_framework import generics
from .serializers import *
from rest_framework import filters
from django_filters import rest_framework as filter
from NOGA.utils import *
from .filters import *
# Create your views here.

class BranchsAPIView(generics.ListAPIView , generics.ListCreateAPIView ):
    queryset= Branch.objects.all()
    serializer_class = BranchSerializer
    pagination_class = Paginator
    filter_backends = [filter.DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
    filterset_fields = ["id" , "number" ,"city" , "area" , "street" , "manager"]
    search_fields = ["id" , "number" , "location"  , "area" , "street" ]
    ordering_fields = ["id" , "number" ,"city" , "area" , "street" , "manager"]
    
    
class BranchAPIView( generics.RetrieveAPIView, generics.DestroyAPIView , generics.UpdateAPIView ):
    queryset= Branch.objects.all()
    serializer_class = BranchSerializer


class CitiesAPIView(generics.ListAPIView , generics.ListCreateAPIView ):
    queryset= City.objects.all()
    serializer_class = CitySerializer
    filter_backends = [filter.DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
    pagination_class = Paginator
    filterset_fields = ["id" ,"city_name"]
    search_fields = ["id" , "city_name"]
    ordering_fields = ["id" ,"city_name"]
  
class CityAPIView( generics.RetrieveAPIView, generics.DestroyAPIView , generics.UpdateAPIView ):
    queryset= City.objects.all()
    serializer_class = CitySerializer

class BranchProductsAPIView(generics.ListAPIView):
    queryset = Branch_Products.objects.all()
    serializer_class = BranchProductsSerializer
    filter_backends=[filter.DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
    filterset_class = BranchProductFilter  
    pagination_class = Paginator
    search_fields = [
        "id",
        "product__product__product__product_name",
        "product__product__quantity",
        "product__product__selling_price",
        "product__product__wholesale_price",
        "product__product__options__option",
        # "options__unit__unit",
        "product__product__options__attribute__attribute", 
        "product__product__sku"
    ]
    ordering_fields = [
        "product__id",
        "product__product__product_name",
        "product__quantity",
        "product__selling_price",
        "product__wholesale_price",
        "product__options__option",
        # "options__unit__unit",
        "product__options__attribute__attribute",
        "product__sku"
    ]
    