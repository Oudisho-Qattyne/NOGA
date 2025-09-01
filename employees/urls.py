from django.urls import path , include , re_path
from .views import *
work_list=WorkScheduleAPIView.as_view({
    'get':'list',
    'post':'create'
})
work_detail=WorkScheduleAPIView.as_view({
    'get':'retrieve',
    'put':'update',
    'delete': 'destroy',
})



urlpatterns = [

    path('',EmployeesApiView.as_view()),
    path('<int:pk>' , EmployeeApiView.as_view() ),
    
    path('job_types/' , Job_TypesView.as_view()),
    path('job_types/<int:pk>' , Job_TypeView.as_view() ),

    path('work_schedules',work_list),
    path('work_schedules/<int:pk>',work_detail),
    
    path('attendance',AttendanceAPIView.as_view({'get': 'list'})),
    path('attendance/check_in',AttendanceAPIView.as_view({'post':'check_in'}),name='check_in'),
    path('attendance/check_out',AttendanceAPIView.as_view({'post':'check_out'}),name='check_out'),

    path('vecations',VecationsAPIView.as_view()),
    path('vecations/<int:pk>',VecationAPIView.as_view()),

    path('salaries',SalaryAPIView.as_view(),name='salary_list'),
    path('salaries/employee/<int:employee_id>',SalaryAPIView.as_view(),name='salary_by_employee'),

    path('available_managers',getAvailableManagers)
]