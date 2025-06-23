from django.urls import path , include , re_path
from .views import *
urlpatterns = [
    path('discounts' , DiscountsAPIView.as_view()),
    path('discounts/<int:pk>' , DiscountAPIView.as_view()),

]