from django.urls import path , include , re_path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [

    path('mobile/register' , ClientRrgisterAPIView.as_view()),
    path('employees/register' , EmployeeRrgisterAPIView.as_view()),

    path('mobile/login', ClientTokenObtainPairView.as_view() , name='token_obtain_pair'),
    path('employees/login', EmployeeTokenObtainPairView.as_view() , name='token_obtain_pair'),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),

]