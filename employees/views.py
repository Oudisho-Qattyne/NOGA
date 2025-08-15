from django.shortcuts import render
from .models import *
from rest_framework import generics , status , filters
from .serializers import *
from django_filters import rest_framework as filter
from rest_framework.response import Response
from rest_framework import generics,filters,viewsets,permissions,status
from rest_framework.decorators import action , api_view
from django.utils import timezone
from datetime import datetime,timedelta
import io
from PIL import Image
import numpy as np
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


class WorkScheduleAPIView(viewsets.ModelViewSet):
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    # permission_classes = [permissions.IsAuthenticated]
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_active == True:
            workSchedule = WorkSchedule.objects.exclude(id=instance.id).first()
            workSchedule.is_active = True
            workSchedule.save()
        return super().destroy(request, *args, **kwargs)

class AttendanceAPIView(viewsets.ModelViewSet):
    queryset=Attendance.objects.all()
    serializer_class = AttendanceSerializer
    @action(detail=False, methods=['post'])
    def check_in(self, request):
        image_file = request.FILES.get('image')
        employee_id = None
        if image_file:
            image_bytes = image_file.read()
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image_np = np.array(image)
            result = recognize(image_np , "mediafiles/pickle")
            if not result.isdigit():
                return Response({'error': result}, status=status.HTTP_400_BAD_REQUEST)
            employee_id = result
        else:
            employee_id = request.data.get('employee')
            if not employee_id:
                return Response({'employee':'Employee ID is required'},status=status.HTTP_400_BAD_REQUEST)
        employee = None        
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({'error':'Employee not found'},status=status.HTTP_404_NOT_FOUND)
        
        now=timezone.now()
        today_date=now.date()
        today=now.weekday()
        schedule=WorkSchedule.objects.filter(is_active=True).first()
        if not schedule:
            return Response({'error':'no active schedule found'},status=status.HTTP_404_NOT_FOUND)
        try:
            work_day=WorkDay.objects.get(schedule=schedule,day=today)
        except WorkDay.DoesNotExist:
            return Response({'error':'No work schedule for today'},status=status.HTTP_404_NOT_FOUND)
        scheduled_start=datetime.combine(now,work_day.start_time).replace(tzinfo=timezone.get_current_timezone())
        delay_minutes=(now-scheduled_start).total_seconds()/60
        # print("delay_minutes" , delay_minutes , now)
        status_text='on_time' if delay_minutes<=30 else 'late'
        # print(delay_minutes<=30 , status_text)
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today_date,
            defaults={
                'status': 'present', 
                'check_in_status':status_text
                }
        )
        active_logs=attendance.logs.filter(check_out__isnull=True)
        if active_logs.exists():
            log=active_logs.first()
            log_serializer=AttendanceLogSerializer(log)
            return Response({'error':'there is an active check in',
                                'active_log_id':log.id,
                                'check_in_time':log_serializer.data})

        log=AttendanceLog.objects.create(
            attendance=attendance,
            check_in=now,
        )
        log_serializer=AttendanceLogSerializer(log)
        
        return Response({'status':'checked in successfully',
                            'log':log_serializer.data,
                            'delay_minutes':round(delay_minutes,2)},status=status.HTTP_201_CREATED)
        
    @action(detail=False,methods=['post'])
    def check_out(self,request):
        image_file = request.FILES.get('image')
        employee_id = None
        if image_file:
            image_bytes = image_file.read()
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image_np = np.array(image)
            result = recognize(image_np , "mediafiles/pickle")
            if not result.isdigit():
                return Response({'error': result}, status=status.HTTP_400_BAD_REQUEST)
            employee_id = result
        else:
            employee_id = request.data.get('employee')
            if not employee_id:
                return Response({'employee':'Employee ID is required'},status=status.HTTP_404_NOT_FOUND)
        employee = None        
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({'error':'Employee not found'},status=400)
        
        try:
            attendance = Attendance.objects.get(
                employee=employee,
                date=timezone.now().date()
            )
        except (Attendance.DoesNotExist):
                return Response({'error':'No attendance record found for today'},
                                 status=status.HTTP_404_NOT_FOUND)
            
        active_log=attendance.logs.filter(check_out__isnull=True).first()
        if not active_log:
            return Response({'error': 'No active check in log found. Maybe already checked out?'},status=status.HTTP_400_BAD_REQUEST) 
        now=timezone.now()
        today_date=now.date()
        today=now.weekday()
        schedule=WorkSchedule.objects.filter(is_active=True).first()
        if not schedule:
            return Response({'error':'no active schedule found'},status=status.HTTP_404_NOT_FOUND)
        try:
            work_day=WorkDay.objects.get(schedule=schedule,day=today)
        except WorkDay.DoesNotExist:
            return Response({'error':'No work schedule for today'},status=status.HTTP_404_NOT_FOUND)
        scheduled_end=datetime.combine(now,work_day.end_time).replace(tzinfo=timezone.get_current_timezone())
        delay_minutes=(now-scheduled_end).total_seconds()/60
        status_text='on_time' if scheduled_end<=now else 'left_early'
        if attendance.logs.count() > 1:
            status_text='left_early'

        attendance.check_out_status = status_text

        active_log.check_out=now
        active_log.save()
        attendance.save()
        log_serializer=AttendanceLogSerializer(active_log)
        return Response({'status':'Check out successfully','log':log_serializer.data},
                        status=status.HTTP_200_OK)


class VecationsAPIView(generics.ListCreateAPIView):
    queryset=Vecation.objects.all()
    serializer_class=VecationSerializer

class VecationAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Vecation.objects.all()
    serializer_class=VecationSerializer

class SalaryAPIView(generics.ListAPIView):
    queryset=Salary.objects.all()
    serializer_class=SalarySerializer
    def get_queryset(self):
        employee_id=self.kwargs.get('employee_id' , None)
        if employee_id is not None:
            return Salary.objects.filter(employee__id=employee_id)
        return Salary.objects.all()
    

@api_view(['GET'])
def getAvailableManagers(request):
    employees = Employee.objects.all()
    managers = employees.filter(job_type = 4)
    serializedManagers = EmployeeSerializer(managers , many=True)
    managers = serializedManagers.data
    
    branches = Branch.objects.all()
    serializedBranches = BranchSerializer(branches , many=True)
    branches = serializedBranches.data
    
    unAvailableManagers = [branch['manager'] for branch in branches ]
    availableManagers = [manager for manager in managers if manager['id'] not in unAvailableManagers ]
    
    
    
    # managers = Employee.objects.all()
    # availableManagers = managers.filter(job_type = 4 , branch = "null")
    # availableManagers = EmployeeSerializer(availableManagers , many=True)
    # print(availableManagers.data)
    return Response({
        "results" : availableManagers
    })
    
    