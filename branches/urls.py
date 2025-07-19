from django.urls import path , include , re_path
from .views import *
urlpatterns = [
    
    path('',BranchsAPIView.as_view()),
    path('<int:pk>' , BranchAPIView.as_view() ),
    
    path('cities',CitiesAPIView.as_view()),
    path('cities/<int:pk>' , CityAPIView.as_view() ),

    path('products/' , BranchProductsAPIView.as_view() ),
    path('products/<int:pk>' , CityAPIView.as_view() ),
]