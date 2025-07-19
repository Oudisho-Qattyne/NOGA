from django.db import models
from NOGA.utils import *
from branches.models import Branch
from datetime import date,timedelta
# Create your models here.


class Job_Type(models.Model):
    job_type=models.CharField(max_length=100 , unique=True)
    def __str__(self) -> str:
        
        return self.job_type


class Employee(models.Model):
    def __str__(self) -> str:
        return self.first_name + " " + self.middle_name + " " + self.last_name
    def full_name(self):
        return self.__str__()
    
    national_number=models.IntegerField(unique=True)
    first_name=models.CharField(max_length=100)
    middle_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    email=models.EmailField(max_length=50 , default="test@gmail.com")
    birth_date=models.DateField()
    gender=models.BooleanField()
    base_salary=models.DecimalField(max_digits=10,decimal_places=2)
    address=models.CharField(max_length=50)
    phone=models.CharField(max_length=100)
    date_of_employment=models.DateField()
    job_type=models.ForeignKey(Job_Type,on_delete=models.PROTECT,default=1)        
    branch = models.ForeignKey("branches.Branch" ,on_delete=models.SET_NULL , null=True)
    image = models.ImageField(upload_to=upload_to, blank=True, null=True , validators=[validate_image_size])

class WorkSchedule(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"
    
class WorkDay(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    schedule=models.ForeignKey(WorkSchedule,on_delete=models.CASCADE,related_name='work_days')
    day = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_working_day=models.BooleanField(default=True)

    class Meta:
        unique_together=['schedule','day']
    
    def __str__(self):
        return f"{self.get_day_display()}({self.schedule})"
    
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee} - {self.date}"
    
class AttendanceLog(models.Model):
    attendance=models.ForeignKey(Attendance,on_delete=models.CASCADE,related_name='logs')
    check_in = models.DateTimeField(null=True, blank=True,verbose_name='وقت الدخول')
    check_out = models.DateTimeField(null=True, blank=True, verbose_name='وقت الخروج')

    class Meta:
        ordering=['-check_in']
    def __str__(self):
        return f"{self.attendance.employee.__str__}-{self.check_in}"
    

class Vecation(models.Model):
    VECATION_TYPE=[('paid','مدفوعة'),
                   ('unpaid',' غير مدفوعة')]
    
    DURATION_TYPE=[('daily','يومية'),
                   ('monthly','شهرية')]
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE,related_name='leaves')
    vecation_type=models.CharField(max_length=10,choices=VECATION_TYPE)
    duration_type=models.CharField(max_length=10,choices=DURATION_TYPE)
    start_date=models.DateField()
    end_date=models.DateField()
    created_at=models.DateTimeField(auto_now_add=True)

    def number_of_days(self):
        return (self.end_date-self.start_date).days+1
    
    def __str__(self):
        return f"{self.employee.full_name}|{self.vecation_type}|{self.start_date}-{self.end_date}" 
    

class Salary(models.Model):
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE,related_name='salary_list')
    month=models.IntegerField()
    year=models.IntegerField()
    base_salary=models.DecimalField(max_digits=10,decimal_places=2)
    final_salary=models.DecimalField(max_digits=10,decimal_places=2)
    absent_days=models.IntegerField()
    unpaid_vecation_days=models.IntegerField()
    late_count=models.IntegerField()
    generated_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together=['employee','month','year']
    
    def __str__(self):
        return f"{self.employee.full_name}-{self.month}/{self.year}"
    
def calculate_employee_salary(employee,year,month):
    base_salary=employee.base_salary
    start_date=date(year,month,1)
    end_date=(date(year+(month // 12),(month % 12)+1,1)-timedelta(days=1))
    working_days=WorkDay.objects.filter(is_working_day=True).count()
    day_salary=base_salary/working_days if working_days else 0
    absents=Attendance.objects.filter(employee=employee,
                                            date__range=(start_date,end_date),
                                            status='absent').count()
    unpaid_vecations=Vecation.objects.filter(employee=employee,
                                                vecation_type='unpaid',
                                                start_date__lte=end_date,
                                                end_date__gte=start_date)
    unpaid_days=0
    for vecation in unpaid_vecations:
        actual_start=max(vecation.start_date,start_date)
        actual_end=min(vecation.end_date,end_date)
        delta_days=(actual_end-actual_start).days+1
        if delta_days>0:
            unpaid_days+=delta_days
    
    late_count=Attendance.objects.filter(employee=employee,
                                            date__range=(start_date,end_date),
                                            status='late').count()
    late_deduction=(0.25*day_salary)*late_count
    total_deduction=(absents + unpaid_days)*day_salary + late_deduction
    final_salary=base_salary-total_deduction

    salary,created=Salary.objects.update_or_create(
        employee=employee,
        month=month,
        year=year,
        defaults={'base_salary':base_salary,
                    'final_salary':round(final_salary,2),
                    'absent_days':absents,
                    'unpaid_vecation_days':unpaid_days,
                    'late_count':late_count
        }
        
    )
    return salary