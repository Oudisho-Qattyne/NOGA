from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from django.utils import timezone
from .models import *

scheduler = BackgroundScheduler()


def markAbsentEmployees():
        today=timezone.localdate()
        now=timezone.now()
        today_date=now.date()
        today=now.weekday()
        schedule=WorkSchedule.objects.filter(is_active=True).first()
        if not schedule:
            print({'error':'no active schedule found'})
        else:
            try:
                work_day=WorkDay.objects.get(schedule=schedule,day=today)
                if work_day.is_working_day:
                    attended_ids=Attendance.objects.filter(date=today).values_list('employee_id',flat=True)

                    on_vecation_ids=Vecation.objects.filter(start_date__lte=today,end_date__gte=today).values_list('employee_id',flat=True)

                    for employee in on_vecation_ids:
                        attendance=Attendance.objects.create(
                            employee=employee,
                            date=today
                        )
                        AttendanceLog.objects.create(
                            attendance=attendance,
                            status='on_vecation'
                        )

                    absent_employees=Employee.objects.exclude(id__in=attended_ids).exclude(id__in=on_vecation_ids)
                    for employee in absent_employees:
                        attendance=Attendance.objects.create(
                            employee=employee,
                            date=today,
                            status='absent'
                        )
                        AttendanceLog.objects.create(
                            attendance=attendance,
                        )
            except WorkDay.DoesNotExist:
                print({'error':'No work schedule for today'})
            
        
def generatMonthlySalaries():
        today=timezone.localdate()

        last_month=today.month-1 if today.month>1 else 12
        year=today.year if today.month>1 else today.year-1
        for employee in Employee.objects.all():
            calculate_employee_salary(employee,year,last_month)

scheduler.add_job(generatMonthlySalaries,'cron', day=1, hour=0, minute=0)  

scheduler.add_job(markAbsentEmployees, 'cron',hour=21,minute=31) 

scheduler.start()

# إيقاف scheduler عند إيقاف السيرفر
atexit.register(lambda: scheduler.shutdown())
