from django.shortcuts import render
from .models import *
from rest_framework import generics , status , filters
from .serializers import *
from django_filters import rest_framework as filter
from rest_framework.response import Response

# Create your views here.
    
class EmployeesApiView(generics.ListAPIView,generics.ListCreateAPIView):
    queryset=Employee.objects.all().select_related( 'job_type', 'branch', 'manager_of_branch', 'employee_user')
    serializer_class=EmployeeSerializer
    pagination_class = Paginator
    # parser_classes = (MultiPartParser, FormParser)
    filter_backends=[filter.DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
    filterset_fields=['id' , 'national_number','first_name','middle_name','last_name','email','salary','address','gender','job_type' , 'branch' , 'phone']
    search_fields=['id' , 'national_number','first_name','middle_name','last_name','email','salary','address','gender' , 'phone' ]
    ordering_fields=['id' , 'national_number','first_name','middle_name','last_name','email','salary','address','gender','job_type' , 'branch' , 'phone']
    

class EmployeeApiView( generics.RetrieveAPIView, generics.DestroyAPIView , generics.UpdateAPIView ):
    queryset=Employee.objects.all()
    serializer_class=EmployeeSerializer  


class Job_TypesView(generics.ListAPIView,generics.ListCreateAPIView ):
    queryset=Job_Type.objects.all()
    serializer_class=Job_TypeSerializer
    pagination_class = Paginator
    filter_backends=[filter.DjangoFilterBackend]
    filterset_fields=['id','job_type']

class Job_TypeView( generics.RetrieveAPIView, generics.DestroyAPIView , generics.UpdateAPIView ):
    queryset= Job_Type.objects.all()
    serializer_class = Job_TypeSerializer
    
    def delete(self, request, pk):
        NOT_DELETABLE = ['CEO' , 'HR' , 'Manager' , 'Warehouse Administrator' , 'Sales Officer' ]
        try:
            instance = Job_Type.objects.get(pk=pk)
            if instance.job_type in NOT_DELETABLE :
                return Response({"error": "Object cannot be deleted"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                instance.delete()
                return Response({"message": "Object deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)
