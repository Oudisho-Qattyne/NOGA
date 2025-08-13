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
from .filters import *
from django.db.models import Q
from django.utils import timezone
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
    filter_backends=[filter.DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
    filterset_class = VariantFilter  
    pagination_class = Paginator
    search_fields = [
        "id",
        "product__product_name",
        "quantity",
        "selling_price",
        "wholesale_price",
        "options__option",
        # "options__unit__unit",
        "options__attribute__attribute", 
        "sku"
    ]
    ordering_fields = [
        "id",
        "product__product_name",
        "quantity",
        "selling_price",
        "wholesale_price",
        "options__option",
        # "options__unit__unit",
        "options__attribute__attribute",
        "sku"
    ]
    def get_queryset(self):
        
        queryset = super().get_queryset()
        attribute_names = Attribute.objects.values_list('attribute', flat=True)

        # Convert the QuerySet to a list
        attribute_names_list = list(attribute_names)
        for key, value in self.request.query_params.items():
            if key in attribute_names_list: 
                queryset = queryset.filter(
                options__attribute__attribute=key,
                options__option=value
            )
        return queryset.distinct()
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
    pagination_class = Paginator

class TransportationAPIView(generics.DestroyAPIView , generics.UpdateAPIView , generics.RetrieveAPIView):
    queryset = Transportation.objects.all().order_by('-created_at')
    serializer_class = TransportationSerializer
    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.transportation_status == "packaging":
                Transported_Products.objects.filter(transportation = instance).delete()
                transport_request_instances = Transport_Request.objects.filter(transportation = instance)
                for transport_request_instance in transport_request_instances: 
                    transport_request_instance.request_status = "waiting"
                    for transported_product in transport_request_instance.requested_products:
                        variant_instance = transported_product.product
                        if instance.source != None:
                            variant_instance = Branch_Products.objects.get(branch=instance.source ,product=variant_instance.product.id)
                        variant_instance.quantity = variant_instance.quantity +  transported_product.quantity
                        variant_instance.save()
                        transported_product.product_request_status = "waiting"
                        transported_product.save()
                    transport_request_instance.transportation = None
                    transport_request_instance.save()
                
                super().delete(request, *args, **kwargs)
                return Response({"message": "Transportation deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else :
                return Response({"message": "'The transportation cannot be deleted after it has been transported.'"}, status=status.HTTP_400_BAD_REQUEST)

        except ProtectedError:
            return Response({"message": "Transportation can't be deleted"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def TransportProducts(request , pk):
    
    try:
        transportation_instance = Transportation.objects.get(id=pk)
        if transportation_instance.transportation_status == 'transporting':
            return Response({"Transportation" : "Transportation has already been sent."} , status=status.HTTP_400_BAD_REQUEST)
        if transportation_instance.transportation_status != 'packaging':
            return Response({"Transportation" : "Transportation is not packed yet"} , status=status.HTTP_400_BAD_REQUEST)

        transportation_instance.transportation_status = "transporting"
        transportation_instance.transported_at = timezone.now()
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
        transportation_instance.received_at = timezone.now()
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

class TransportRequestsAPIView(generics.ListAPIView , generics.CreateAPIView):
    queryset = Transport_Request.objects.all().order_by('-created_at')
    serializer_class = TransportRequestSerializer
    pagination_class = Paginator
    

class TransportRequestAPIView(generics.DestroyAPIView , generics.UpdateAPIView):
    queryset = Transport_Request.objects.all()
    serializer_class = TransportRequestSerializer
    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.request_status == "waiting":
                Requested_Products.objects.filter(request=instance).delete()
                super().delete(request, *args, **kwargs)
                return Response({"message": "Request deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else :
                return Response({"message": "'The request cannot be deleted after it has been processed.'"}, status=status.HTTP_400_BAD_REQUEST)

        except ProtectedError:
            return Response({"message": "Request can't be deleted"}, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST'])
def ProcessTransportRequest(request , pk):
    data =None
    transported_products = request.data.get('transported_products' , [])
    if transported_products is None:
        return Response({"transported_products":"This field is required" }, status=status.HTTP_400_BAD_REQUEST)
    if  type(transported_products) != list:
        return Response({"transported_products":"Expected a list of items" }, status=status.HTTP_400_BAD_REQUEST)
    if  len(transported_products) == 0:
        return Response({"transported_products":"This list is empty" }, status=status.HTTP_400_BAD_REQUEST)
    try:
        transport_request = Transport_Request.objects.get(id=pk)
        if transport_request.request_status == "waiting":
            transportation_data = {
            "transported_products":transported_products,
            "destination":transport_request.branch.id,

            }
            transportation_serialized_data = TransportationSerializer(data=transportation_data)
            valid = transportation_serialized_data.is_valid(raise_exception=True)
            requested_products_instances = transport_request.requested_products
            # transported_products_ids = list(product['product'] for product in transported_products)

            is_fully_approved = True
            is_rejected = True
            if valid:
                transportation_instance = transportation_serialized_data.save()
                for requested_product in requested_products_instances:
                    transported_product = find_element_by_id2(transported_products , requested_product.product.id )
                    if transported_product is not None:
                        if transported_product['quantity'] >= requested_product.quantity:
                            requested_product.product_request_status = "fully-approved"
                            is_rejected = False
                        else:
                            requested_product.product_request_status = "partially-approved"
                            is_fully_approved = False
                            is_rejected = False
                    else:
                        requested_product.product_request_status = "rejected"
                        is_fully_approved = False
                    requested_product.save()
                if is_fully_approved:
                    transport_request.request_status = "fully-approved"
                elif is_rejected:
                    transport_request.request_status = "rejected"
                else:
                    transport_request.request_status = "partially-approved"
                transport_request.transportation = transportation_instance
                transport_request.save()
                transport_request_seriaized_data = TransportRequestSerializer(transport_request)
                data = transport_request_seriaized_data.data
        else:
            return Response({"Request" : "This request has already been processed"} , status=status.HTTP_400_BAD_REQUEST)

    except Transport_Request.DoesNotExist:
        return Response({"message" : "Request not found"} , status=status.HTTP_404_NOT_FOUND)
    return Response( data, status=status.HTTP_200_OK)

@api_view(['POST'])
def RejectTransportRequest(request , pk):
    try:
        transport_request = Transport_Request.objects.get(id=pk)
        if transport_request.request_status == "waiting":
            requested_products_instances = transport_request.requested_products
            for requested_product in requested_products_instances:
                requested_product.product_request_status = "rejected"
                requested_product.save()
            transport_request.request_status = "rejected"
            transport_request.save()
            transport_request_seriaized_data = TransportRequestSerializer(transport_request)
            data = transport_request_seriaized_data.data
        else:
            return Response({"Request" : "This request has already been processed"} , status=status.HTTP_400_BAD_REQUEST)
    except Transport_Request.DoesNotExist:
        return Response({"message" : "Request not found"} , status=status.HTTP_404_NOT_FOUND)

    return Response( data, status=status.HTTP_200_OK)
