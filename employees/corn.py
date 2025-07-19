from django_cron import CronJobBase,Schedule
from django.utils import timezone
from .models import *
class MarkAbsentEmployeesCornJob(CronJobBase):
    RUN_EVERY_MINS=1440
    Schedule(run_every_mins=RUN_EVERY_MINS)
    code='employees.mark_absent_employees_corn'
    def do(self):
        today=timezone.localdate()
        attended_ids=Attendance.objects.filter(date=today).values_list('employee_id',flat=True)

        on_vecation_ids=Vecation.objects.filter(start_date__lte=today,end_date__gte=today).values_list('employee_id',flat=True)
        for employee in on_vecation_ids:
            attendance=Attendance.objects.create(
                employee=employee,
                date=today
            )
            AttendanceLog.objects.create(
                attendance=attendance,
                status='present'
            )

        absent_employees=Employee.objects.exclude(id__in=attended_ids).exclude(id__in=on_vecation_ids)
        for employee in absent_employees:
            attendance=Attendance.objects.create(
                employee=employee,
                date=today,
            )
            AttendanceLog.objects.create(
                attendance=attendance,
                status='absent'
            )
        print(f"{absent_employees.count()} employee marked as absent for {today}")
    

class GeneratMonthlySalaries(CronJobBase):
    RUN_EVERY_MINTS=1440
    Schedule(run_every_mins=RUN_EVERY_MINTS)
    code='employees.generate_monthly_salaries'
    def do(self):
        today=timezone.localdate()
        if today.day !=1:
            return 
        last_month=today.month-1 if today.month>1 else 12
        year=today.year if today.month>1 else today.year-1
        for employee in Employee.objects.all():
            calculate_employee_salary(employee,year,last_month)
        