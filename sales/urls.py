from django.urls import path , include , re_path
from .views import *
urlpatterns = [
    path('discounts' , DiscountsAPIView.as_view()),
    path('discounts/<int:pk>' , DiscountAPIView.as_view()),

    path('offers' , OffersAPIView.as_view()),
    path('offers/<int:pk>' , OfferAPIView.as_view()),

    path('coupons' , CouponsAPIView.as_view()),
    path('coupons/<int:pk>' , CouponAPIView.as_view()),

    path('purchases' , PurchasesAPIView.as_view()),
    path('purchases/<int:pk>' , PurchaseAPIView.as_view()),

    path('customers' ,CustomersAPIVIew.as_view()),
    path('customers/<int:pk>' , CustomerAPIVIew.as_view()),
]