from django.urls import path , include , re_path
from .views import *
urlpatterns = [
    path('discounts' , DiscountsAPIView.as_view()),
    path('discounts/<int:pk>' , DiscountAPIView.as_view()),

    # path('offers' , OffersAPIView.as_view()),
    # path('offers/<int:pk>' , OfferAPIView.as_view()),

    path('coupons' , CouponsAPIView.as_view()),
    path('coupons/<int:pk>' , CouponAPIView.as_view()),

    path('purchases' , PurchasesAPIView.as_view()),
    path('purchases/<int:pk>' , PurchaseAPIView.as_view()),

    path('purchase/<int:pk>/process' , ProcessPurchase),
    path('purchase/<int:pk>/complete' , CompletePurchase),
    path('purchase/<int:pk>/cancel' , CancelPurchase),

    path('customers' ,CustomersAPIVIew.as_view()),
    path('customers/<int:pk>' , CustomerAPIVIew.as_view()),
    
    path('assoication-rules',AssociationRuleViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('assoication-rules/<int:pk>/recommendations',AssociationRuleViewSet.as_view({'get':'recommendations'})),
    path('hello',hello),
    


    
    path('income',TotalIncome),
    path('income/branches',TotalIncomeAllBranch),
    path('income/branches/<int:branch_id>',TotalIncomePerBranch),
    
    path('earnings',TotaEarnings),
    path('earnings/branches',TotalEarningAllBranch),
    path('earnings/branches/<int:branch_id>',TotalEarningPerBranch),
    
    path('purchaced-products-quantities',TotalProducts),
    path('purchaced-products-quantities/branches',TotalProductsAllBranch),
    path('purchaced-products-quantities/branches/<int:branch_id>',TotalProductsPerBranch),
    # path('customers/count',getCustomersNumber),
    
]