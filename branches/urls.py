from django.urls import path , include , re_path
from .views import *
urlpatterns = [
    
    path('',BranchsAPIView.as_view()),
    path('<int:pk>' , BranchAPIView.as_view() ),
    
    path('cities',CitiesAPIView.as_view()),
    path('cities/<int:pk>' , CityAPIView.as_view() ),

    path('products/' , BranchProductsAPIView.as_view() ),
    path('products/<int:pk>' , BranchProductsAPIView.as_view() ),
    path('find_nearest_branch' , find_nearest_branch_with_product),

    path('cameras' , CamerasApiView.as_view() ),
    path('cameras/<int:pk>' , CameraApiView.as_view() ),

    path('branch-visitors/', BranchVisitorsListView.as_view(), name='branch-visitors-list'),
    path('branch-visitors/<int:pk>/', BranchVisitorsRetrieveView.as_view(), name='branch-visitors-detail'),
    



]