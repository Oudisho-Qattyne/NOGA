from tkinter.tix import STATUS
from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics,filters,viewsets,permissions,status
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated 
from django_filters import rest_framework as filter
from django.db.models import Prefetch
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound,ValidationError
# Create your views here.


class ClientProfileAPIView(generics.ListAPIView,generics.ListCreateAPIView):
    queryset=Client_Profile.objects.all()
    serializer_class=ClientProfileSerializer
    permission_classes=[IsAuthenticated]
    pagination_class = Paginator
    # parser_classes = (MultiPartParser, FormParser)
    filter_backends=[filter.DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
    filterset_fields=['national_number','first_name','middle_name','last_name','address','gender']
    search_fields=['national_number','first_name','middle_name','last_name','email','address','birth_date','gender' , 'phone' ]
    ordering_fields=['national_number','first_name','middle_name','last_name','email','address','birth_date','gender' , 'phone']


class CommentsAPIView(generics.ListCreateAPIView):
    queryset=Comment.objects.all()
    serializer_class=CommentSerializer
    permission_classes=[IsAuthenticated]
class CommentAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Comment.objects.all()
    serializer_class=CommentSerializer
    permission_classes=[IsAuthenticated]


class LikesAPIView(generics.ListCreateAPIView):
    queryset=Like.objects.all()
    serializer_class=LikeSerializer
    permission_classes=[IsAuthenticated]
class LikeAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Like.objects.all()
    serializer_class=LikeSerializer
    permission_classes=[IsAuthenticated]

class ToggleSaveView(generics.CreateAPIView):
    serializer_class=Saveserializer
    permission_classes=[IsAuthenticated]

    def create(self, request, *args, **kwargs):
        product_id=request.data.get('product')
        try:
            product=Product.objects.get(id=product_id)
            print(product)
        except Product.DoesNotExist:
            return Response( {"detail":"product not found"},status=status.HTTP_404_NOT_FOUND)
        save_exists=Save.objects.filter(user=request.user,product=product).exists()
        if save_exists:
                save_exists=Save.objects.filter(user=request.user,product=product).delete()
                return Response({"status":"Removed save"},
                                status=status.HTTP_200_OK)

        else:
            Save.objects.create(user=request.user,product=product)
            return Response({"status":"Saved successfully "},status=status.HTTP_200_OK)
        

class ProductSimpleAPIView(generics.ListAPIView):
    queryset=Product.objects.all().prefetch_related('reviews')
    serializer_class=ProductSimpleSerializer
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]

    def reviews(self):
        product = self.get_object() 
        reviews = product.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data) 

class UserSavedProductsAPIView(generics.RetrieveAPIView):
    serializer_class=UserSavedProductsSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return User.objects.prefetch_related(Prefetch(
            'save_set',
            queryset=Save.objects.select_related('product'),
            to_attr='saves_with_products'
        )).filter(pk=self.request.user.pk)
    
    def get_object(self):
        return self.get_queryset().first()
    


class ReviewAPIView(viewsets.ModelViewSet):
    queryset=Review.objects.all()
    serializer_class=ReviewSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        product_id=self.kwargs.get('product_pk')
        product_exists=Product.objects.filter(pk=product_id).exists()
        if product_exists:
            return Review.objects.filter(product_id=product_id)
        else:
            raise FileNotFoundError(f'{product_id} not found')
        
    def perform_create(self, serializer):
        product_id=self.kwargs.get('product_pk')
        product=get_object_or_404(Product,pk=product_id)
        if Review.objects.filter(product=product,user=self.request.user).exists():
            raise ValidationError({"error":"exists already"},code=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=self.request.user,product=product)

    def update(self,request,*args,**kwargs):
        review=self.get_object()
        print(review.user)
        if review.user!=request.user:
            return Response({"error":"Sorry,you do not have permission to edit this rating"},status=status.HTTP_403_FORBIDDEN)
        return super().update(request,*args,**kwargs)
    
    def destroy(self, request, *args, **kwargs):
        review=self.get_object()
        if review.user!=request.user:
            return Response({"error":"Sorry,you do not have permission to delete this rating"},status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
