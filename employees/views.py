from django.shortcuts import render
from .models import *
from rest_framework import generics , status , filters
from .serializers import *
from django_filters import rest_framework as filter
from rest_framework.response import Response
from rest_framework import generics,filters,viewsets,permissions,status
from rest_framework.decorators import action
from django.utils import timezone
from datetime import datetime,timedelta
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

class AttendanceAPIView(viewsets.ModelViewSet):
    queryset=Attendance.objects.all()
    serializer_class = AttendanceSerializer
    @action(detail=False, methods=['post'])
    def check_in(self, request):
        employee_id = request.data.get('employee')
        if not employee_id:
            return Response({'error':'Employee ID is required'},status=status.HTTP_404_NOT_FOUND)
        
        employee = Employee.objects.get(id=employee_id)
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
        status_text='present' if delay_minutes<=30 else 'late'
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today_date,
            defaults={ 'status':status_text}
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

        employee_id=request.data.get('employee')
        if not employee_id:
            return Response({'error':'Employee not found'},status=400)
        employee = Employee.objects.get(id=employee_id)
        
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
      
        active_log.check_out=timezone.now()
        active_log.save()
       
        log_serializer=AttendanceLogSerializer(active_log)
        return Response({'status':'Check out successfully','log':log_serializer.data},
                        status=status.HTTP_200_OK)


class VecationAPIView(generics.ListCreateAPIView):
    queryset=Vecation.objects.all()
    serializer_class=VecationSerializer

class SalaryAPIView(generics.ListAPIView):
    queryset=Salary.objects.all()
    serializer_class=SalarySerializer
    def get_queryset(self):
        employee_id=self.kwargs['employee_id']
        return Salary.objects.filter(employee__id=employee_id)