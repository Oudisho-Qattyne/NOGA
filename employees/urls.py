from django.urls import path , include , re_path
from .views import *

urlpatterns = [

    path('',EmployeesApiView.as_view()),
    path('<int:pk>' , EmployeeApiView.as_view() ),
    
    path('job_types/' , Job_TypesView.as_view()),
    path('job_types/<int:pk>' , Job_TypeView.as_view() ),
]