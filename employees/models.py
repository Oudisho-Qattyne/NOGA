from django.db import models
from NOGA.utils import *
from branches.models import Branch
from datetime import date,timedelta
from decimal import Decimal
from django.db.models import Q

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
    salary=models.DecimalField(max_digits=10,decimal_places=2)
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
        ('on_vecation', 'On Vecation'),
    ]
    CHECK_IN_STATUS = [
        ('on_time', 'On Time'),
        ('late', 'Late'),
    ]
    CHECK_OUT_STATUS = [
        ('on_time', 'On Time'),
        ('left_early', 'Left Early'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    check_in_status = models.CharField(max_length=20, choices=CHECK_IN_STATUS)
    check_out_status = models.CharField(max_length=20, choices=CHECK_OUT_STATUS)
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
    late_or_left_early_count=models.IntegerField()
    generated_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together=['employee','month','year']
    
    def __str__(self):
        return f"{self.employee.full_name}-{self.month}/{self.year}"
    
def count_specific_weekday(year, month, weekdays_to_count):
    current_day = date(year, month, 1)
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    
    count = 0
    while current_day < next_month:
        if current_day.weekday() in weekdays_to_count:
            count += 1
        current_day += timedelta(days=1)
    return count

def calculate_work_percentage(work_schedule , attendance):
    try:
        attendance_logs = attendance.logs.all()  # جميع سجلات الدخول والخروج لذلك اليوم
        date = attendance.date
        total_work_seconds = 0
        
        for log in attendance_logs:
            if log.check_in and log.check_out:
                duration = (log.check_out - log.check_in).total_seconds()
                if duration > 0:
                    total_work_seconds += duration
        
        # الحصول على يوم العمل في جدول العمل لهذا اليوم (0=Monday ... 6=Sunday)
        weekday = date.weekday()
        work_day = WorkDay.objects.get(schedule=work_schedule, day=weekday)
        
        official_start = timedelta(hours=work_day.start_time.hour, minutes=work_day.start_time.minute)
        official_end = timedelta(hours=work_day.end_time.hour, minutes=work_day.end_time.minute)
        official_hours = (official_end - official_start).total_seconds() / 3600  # بالساعات
        actual_hours = total_work_seconds / 3600
        
        work_percentage = (actual_hours / official_hours) * 100 if official_hours > 0 else 0
        return round(work_percentage, 2)
    
    except Attendance.DoesNotExist:
        return 0
    except WorkDay.DoesNotExist:
        return 0
    
def calculate_employee_salary(employee,year,month):
    work_schedule=WorkSchedule.objects.filter(is_active=True).first()
    base_salary=employee.salary
    start_date=date(year,month,1)
    end_date=(date(year+(month // 12),(month % 12)+1,1)-timedelta(days=1))
    working_days=list(WorkDay.objects.filter(is_working_day=True , schedule=work_schedule).values_list("day" , flat=True))
    working_days_in_this_month_count = count_specific_weekday(year , month , working_days) 
    day_salary=base_salary/working_days_in_this_month_count if working_days_in_this_month_count else 0
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

    late_or_left_early = Attendance.objects.filter(
        employee=employee,
        date__range=(start_date, end_date),
    ).filter(
        Q(check_in_status='late') | Q(check_out_status='left_early')
    )
    # حساب الراتب في الأيام الي تم فيها تقطيع الدوام
    late_or_left_early_days_salary = 0
    for atte in late_or_left_early:
        percentage_of_this_day = calculate_work_percentage(work_schedule , atte ) 
        salary_of_this_day =Decimal( day_salary * Decimal(percentage_of_this_day)).quantize(Decimal('0.01'))
        late_or_left_early_days_salary += salary_of_this_day
    total_deduction=(absents + unpaid_days + late_or_left_early.count() )*day_salary 
    final_salary=base_salary-total_deduction+late_or_left_early_days_salary

    salary,created=Salary.objects.update_or_create(
        employee=employee,
        month=month,
        year=year,
        defaults={'base_salary':base_salary,
                    'final_salary':round(final_salary,2),
                    'absent_days':absents,
                    'unpaid_vecation_days':unpaid_days,
                    'late_or_left_early_count':late_or_left_early.count()
        }
        
    )
    return salary.final_salary , created