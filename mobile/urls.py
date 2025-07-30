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
comment_list = CommentAPIView.as_view({
    'get':'list',
    'post':'create'
})
comment_detail = CommentAPIView.as_view({
    'get':'retrieve',
    'put':'update',
    'delete':'destroy'
})
replay_list = ReplayAPIView.as_view({
    'get':'list',
    'post':'create'
})
replay_detail = ReplayAPIView.as_view({
    'get':'retrieve',
    'put':'update',
    'delete':'destroy'
})
urlpatterns = [
    path('clients-profile' , ClientProfileAPIView.as_view()),

    # path('comments',CommentsAPIView.as_view()),
    # path('comments/<int:pk>',CommentAPIView.as_view()),


    path('user/likes' , UserLikedProductsAPIView.as_view()),
    path('like/toggle' , ToggleLikeView.as_view()),

    path('products',ProductSimpleAPIView.as_view()),
    path('save/toggle',ToggleSaveView.as_view()),

    path('user/saves',UserSavedProductsAPIView.as_view()),


    path('products/<int:product_pk>/reviews',review_list),
    path('products/<int:product_pk>/reviews/<int:pk>',review_detail),

    
    path('products/<int:product_pk>/comments',comment_list),
    path('products/<int:product_pk>/comments/<int:pk>',comment_detail),
    path('products/<int:product_pk>/comments/<int:comment_pk>/replaies',replay_list),
    path('products/<int:product_pk>/comments/<int:comment_pk>/replaies/<int:pk>',replay_detail),

    ]