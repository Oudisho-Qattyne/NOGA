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
    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            return Response({"message": "Object deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Response({"message": "Object can't be deleted"}, status=status.HTTP_400_BAD_REQUEST)

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
    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            return Response({"message": "Object deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Response({"message": "Object can't be deleted"}, status=status.HTTP_400_BAD_REQUEST)

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
    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            return Response({"message": "Object deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Response({"message": "Object can't be deleted"}, status=status.HTTP_400_BAD_REQUEST)

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
    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            return Response({"message": "Object deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Response({"message": "Object can't be deleted"}, status=status.HTTP_400_BAD_REQUEST)


class OptionsAPIView(generics.ListAPIView , generics.CreateAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    pagination_class = Paginator
    filter_backends=[filter.DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
    filterset_fields=["id" , "option" , "attribute" ]
    search_fields=["id" , "option" , "attribute"]
    ordering_fields=["id" , "option" , "attribute" ]

class OptionAPIView(generics.DestroyAPIView , generics.UpdateAPIView , generics.RetrieveAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            return Response({"message": "Object deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Response({"message": "Object can't be deleted"}, status=status.HTTP_400_BAD_REQUEST)


class VariantsAPIView(generics.ListAPIView , generics.CreateAPIView):
    queryset = Variant.objects.all()
    serializer_class = VariantSerializers

class VariantAPIView(generics.DestroyAPIView , generics.UpdateAPIView , generics.RetrieveAPIView):
    queryset = Variant.objects.all()
    serializer_class = VariantSerializers
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.options.filter(attribute__is_categorical=False).delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            return Response({"message": "Object deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Response({"message": "Object can't be deleted"}, status=status.HTTP_400_BAD_REQUEST)
