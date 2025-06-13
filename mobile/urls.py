from django.urls import path , include , re_path
from .views import * 
from rest_framework.routers import DefaultRouter
review_list=ReviewAPIView.as_view({
    'get':'list',
    'post':'create'
})
review_detail=ReviewAPIView.as_view({
    'get':'retrieve',
    'put':'update',
    'delete':'destroy'
})
urlpatterns = [
    path('clients-profile' , ClientProfileAPIView.as_view()),

    path('comments',CommentsAPIView.as_view()),
    path('comment/<int:pk>',CommentAPIView.as_view()),

    path('likes',LikesAPIView.as_view()),
    path('like/<int:pk>',LikeAPIView.as_view()),

    path('products',ProductSimpleAPIView.as_view()),
    path('save/toggle',ToggleSaveView.as_view()),
    path('user/saves',UserSavedProductsAPIView.as_view()),


    path('product/<int:product_pk>/reviews',review_list),
    path('product/<int:product_pk>/reviews/<int:pk>',review_detail),

    ]