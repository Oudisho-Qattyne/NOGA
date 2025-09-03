from django.urls import path , include , re_path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [

    path('mobile/register' , ClientRrgisterAPIView.as_view()),
    path('employees/register' , EmployeeRrgisterAPIView.as_view()),

    path('mobile/login', ClientTokenObtainPairView.as_view() , name='token_obtain_pair'),
    path('employees/login', EmployeeTokenObtainPairView.as_view() , name='token_obtain_pair'),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),

    path('mobile/logout', LogoutView.as_view() , name='logout'),
    path('employees/logout', LogoutView.as_view() , name='logout'),

    path('verify-email/<str:token>/', VerifyEmailAPIView.as_view(), name='verify-email'),

    path('reset-password', PasswordResetRequestAPIView.as_view(), name='reset-password'),
    path('reset-password-confirm/<int:uid>/<str:token>/', password_reset_confirm, name='password_reset_confirm'),
    path('password_reset_invalid', password_reset_invalid, name='password_reset_invalid'),
    path('password_set', password_set, name='password_set'),
]