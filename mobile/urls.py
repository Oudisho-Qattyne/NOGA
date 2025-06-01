from django.urls import path , include , re_path
from .views import * 
urlpatterns = [
    path('clients-profile' , ClientProfileAPIView.as_view())
]