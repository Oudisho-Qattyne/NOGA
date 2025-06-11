from django.shortcuts import render
from rest_framework.views import APIView , Response , status
from rest_framework import generics 
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated 
from rest_framework import filters
from django_filters import rest_framework as filter
from NOGA.utils import *
from rest_framework.decorators import api_view , permission_classes

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

class TransportationsAPIView( generics.CreateAPIView , generics.ListAPIView ):
    queryset = Transportation.objects.all()
    serializer_class = TransportationSerializer

class TransportationAPIView(generics.DestroyAPIView , generics.UpdateAPIView , generics.RetrieveAPIView):
    queryset = Transportation.objects.all()
    serializer_class = TransportationSerializer

@api_view(['POST'])
def TransportProducts(request , pk):
    
    try:
        transportation_instance = Transportation.objects.get(id=pk)
        if transportation_instance.transportation_status == 'transporting':
            return Response({"Transportation" : "Transportation has already been sent."} , status=status.HTTP_400_BAD_REQUEST)
        if transportation_instance.transportation_status != 'packaging':
            return Response({"Transportation" : "Transportation is not packed yet"} , status=status.HTTP_400_BAD_REQUEST)

        transportation_instance.transportation_status = "transporting"
        transportation_instance.save()

    except Transportation.DoesNotExist:
        Response({"message" : "Transportation not found"} , status=status.HTTP_404_NOT_FOUND)

    return Response({"message" : f'Transportation {pk} is transporting' })


@api_view(['POST'])
def ReceiveTransportation(request , pk):
    
    try:
        transportation_instance = Transportation.objects.get(id=pk)
        if transportation_instance.transportation_status == 'delivered':
            return Response({"Transportation" : "Transportation has already been received"} , status=status.HTTP_400_BAD_REQUEST)
        if transportation_instance.transportation_status != 'transporting':
            return Response({"Transportation" : "Transportation is not sent yet"} , status=status.HTTP_400_BAD_REQUEST)

        if 'code' not in request.data:
            return Response({"code" : "The code is required"} , status=status.HTTP_400_BAD_REQUEST)
        
        code = request.data['code']

        if code != transportation_instance.code:
            return Response({"code" : "The code does not match"} , status=status.HTTP_400_BAD_REQUEST)
        
        transportation_instance.transportation_status = "delivered"
        transportation_instance.save()

    except Transportation.DoesNotExist:
        Response({"message" : "Transportation not found"} , status=status.HTTP_404_NOT_FOUND)

    return Response({"message" : f'Transportation {pk} is delivered' })


@api_view(['POST'])
def ConfirmTransportation(request , pk):
   
    try:
        transportation_instance = Transportation.objects.get(id=pk)
        if transportation_instance.transportation_status == 'confirmed':
            return Response({"Transportation" : "Transportation has already been confirmed"} , status=status.HTTP_400_BAD_REQUEST)
        if transportation_instance.transportation_status != 'delivered':
            return Response({"Transportation" : "Transportation is not delivered yet"} , status=status.HTTP_400_BAD_REQUEST)

        if 'received_products' not in request.data:
            return Response({"received_products" : "The received products are required"} , status=status.HTTP_400_BAD_REQUEST)
        
        received_products = request.data['received_products']

        errors = []

        for received_product in received_products:
            received_product['transportation'] = transportation_instance.id
            received_product_serialized_data = ReceivedProductSerializer(data=received_product)
            valid = received_product_serialized_data.is_valid()
            if not valid:
                errors.append(received_product_serialized_data.errors)

        if len(errors)!=0:
            return Response({"received_product" : errors} , status=status.HTTP_400_BAD_REQUEST)
        
        destination_branch = transportation_instance.destination
        for received_product in received_products:
            received_product['transportation'] = transportation_instance.id
            received_product_serialized_data = ReceivedProductSerializer(data=received_product)
            valid = received_product_serialized_data.is_valid()
            received_product_instance = received_product_serialized_data.save()
            if transportation_instance.destination != None:
                try:
                    branch_product = Branch_Products.objects.get(branch=destination_branch , product=received_product_instance.product)
                    branch_product.quantity = branch_product.quantity +  received_product_instance.quantity
                    branch_product.save()
                except:
                    branch_product = Branch_Products.objects.create(branch=destination_branch , product=received_product_instance.product, quantity=0)
                    branch_product.quantity = branch_product.quantity + received_product_instance.quantity
                    branch_product.save()
            else:
                variant_instance = received_product_instance.product
                variant_instance.quantity = variant_instance.quantity + received_product_instance.quantity
                variant_instance.save()
        transportation_instance.transportation_status = "confirmed"
        transportation_instance.save()

    except Transportation.DoesNotExist:
        Response({"message" : "Transportation not found"} , status=status.HTTP_404_NOT_FOUND)

    return Response({"message" : f'Transportation {pk} is confirmed' })

