from django.urls import path , include , re_path
from .views import *
urlpatterns = [
    
    path('units' , UnitsAPIView.as_view()),
    path('units/<int:pk>' , UnitAPIView.as_view()),

    path('attributes' , AttributesAPIView.as_view()),
    path('attributes/<int:pk>' , AttributeAPIView.as_view()),
    
    path('categories' , CategroiesAPIView.as_view()),
    path('categories/<int:pk>' , CategroyAPIView.as_view()),

    path('' , ProductsAPIView.as_view()),
    path('<int:pk>' , ProductAPIView.as_view()),

    path('options' , OptionsAPIView.as_view()),
    path('options/<int:pk>' , OptionAPIView.as_view()),

    path('variants' , VariantsAPIView.as_view()),
    path('variants/<int:pk>' , VariantAPIView.as_view()),

]