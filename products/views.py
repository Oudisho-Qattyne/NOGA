from django.shortcuts import render
from rest_framework.views import APIView , Response , status
from rest_framework import generics 
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated 
from rest_framework import filters
from django_filters import rest_framework as filter
from NOGA.utils import *
# Create your views here.


class AttributesAPIView(generics.ListAPIView,generics.ListCreateAPIView):
    queryset=Attribute.objects.all()
    serializer_class=AttributeSerializer
    # permission_classes=[IsAuthenticated]
    pagination_class = Paginator
    filter_backends=[filter.DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
    filterset_fields=['attribute' , 'attribute_type' , 'is_multivalue' , 'is_categorical' , 'has_unit' , 'units' ]
    search_fields=['attribute' , 'attribute_type' , 'is_multivalue' , 'is_categorical' , 'has_unit' , 'units' ]
    ordering_fields=['attribute' , 'attribute_type' , 'is_multivalue' , 'is_categorical' , 'has_unit' , 'units' ]

class AttributeAPIView(generics.DestroyAPIView , generics.UpdateAPIView , generics.RetrieveAPIView):
    queryset=Attribute.objects.all()
    serializer_class=AttributeSerializer
    # permission_classes=[IsAuthenticated]

class UnitsAPIView(generics.ListAPIView,generics.ListCreateAPIView):
    queryset=Unit.objects.all()
    serializer_class=UnitSerializer
    # permission_classes=[IsAuthenticated]
    pagination_class = Paginator
    filter_backends=[filter.DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
 
class UnitAPIView(generics.DestroyAPIView,generics.UpdateAPIView , generics.RetrieveAPIView):
    queryset=Unit.objects.all()
    serializer_class=UnitSerializer
    # permission_classes=[IsAuthenticated]
 
class CategroiesAPIView(generics.ListAPIView , generics.CreateAPIView):
    queryset=Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = Paginator
    filter_backends=[filter.DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
    filterset_fields=['id' , 'category' , 'parent_category' ]
    search_fields=['id' , 'category' , 'parent_category' , 'attributes']
    ordering_fields=['id' , 'category' , 'parent_category' ]

     
class CategroyAPIView(generics.DestroyAPIView , generics.UpdateAPIView , generics.RetrieveAPIView):
    queryset=Category.objects.all()
    serializer_class = CategorySerializer

class ProductsAPIView(generics.ListAPIView , generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = Paginator
    filter_backends=[filter.DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
    filterset_fields=["id" , "product_name" , "category" ]
    search_fields=["id" , "product_name" , "category"]
    ordering_fields=["id" , "product_name" , "category" ]

class ProductAPIView(generics.DestroyAPIView , generics.UpdateAPIView , generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    

class OptionsAPIView(generics.ListAPIView , generics.CreateAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer

class OptionAPIView(generics.DestroyAPIView , generics.UpdateAPIView , generics.RetrieveAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer


class VarientsAPIView(generics.ListAPIView , generics.CreateAPIView):
    queryset = Varient.objects.all()
    serializer_class = VarientSerializers

class VarientAPIView(generics.DestroyAPIView , generics.UpdateAPIView , generics.RetrieveAPIView):
    queryset = Varient.objects.all()
    serializer_class = VarientSerializers
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.options.filter(attribute__is_categorical=False).delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)