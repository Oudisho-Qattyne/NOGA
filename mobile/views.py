from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated 
from rest_framework import filters
from django_filters import rest_framework as filter

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