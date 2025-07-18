from rest_framework import serializers
from .models import *
from products.models import Product
from django.utils import timezone
from django.db.models import Avg
class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Client_Profile
        fields=[ 'national_number','first_name','middle_name','last_name','email','address','birth_date','gender' , 'phone'  , 'image' , 'user'] 
        extra_kwargs = {
            "user" : {'read_only' : True},
        }
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    
class ReplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['user_id','product_id','comment_text','created_at','updated_at']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Comment
        fields=['id' , 'user_id','product_id','comment_text','replay_to','created_at','updated_at' ]
        extra_kwargs = {
            "user_id" : {'read_only' : True},
            "created_at":{'read_only':True},
            "updated_at":{'read_only':True},
            "product_id":{'read_only':True},
        }
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user_id'] = user
        return super().create(validated_data)
    
    
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Like
        fields=['user_id','product_id']
        extra_kwargs = {
            "user_id" : {'read_only' : True},
        }
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user_id'] = user
        return super().create(validated_data)
    

class Saveserializer(serializers.ModelSerializer):
    class Meta:
        model=Save
        fields=['id','user','product','saved_at']
        read_only_fields=['user','saved_at']
    
class UserSavedProductsSerializer(serializers.ModelSerializer):
    saved_products=serializers.SerializerMethodField()
    class Meta:
        model=Save
        fields=['saved_products','saves_at']
    
    def get_saved_products(self,obj):
        saves=Save.objects.filter(user=obj).select_related('product')
        return[
            {'product':ProductSimpleSerializer(save.product).data,
             'saves_at':self.format_datetime(save.saves_at),}
             for save in saves
        ]
    def format_datetime(self,value):
        return timezone.localtime(value).strftime('%Y-%m-%d %H:%M:%S')

class UserLikedProductsSerializer(serializers.ModelSerializer):
    liked_products=serializers.SerializerMethodField()
    class Meta:
        model=Like
        fields=['liked_products']
    
    def get_liked_products(self,obj):
        likes=Like.objects.filter(user_id=obj).select_related('product_id')
        return[
            {'product':ProductSimpleSerializer(like.product_id).data,}
             for like in likes
        ]
    def format_datetime(self,value):
        return timezone.localtime(value).strftime('%Y-%m-%d %H:%M:%S')
  

class ReviewSerializer(serializers.ModelSerializer):
    user=serializers.StringRelatedField(read_only=True)
    rating_display=serializers.SerializerMethodField()
    class Meta:
        model=Review
        fields=['id' , 'user','product','rating','rating_display','comment','created_at','updated_at']
        read_only_fields=['user','product','rating_display','created_at','updated_at']
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    
    def get_rating_display(self,obj):
        return dict(Review.RATING_CHOICES).get(obj.rating)
    
    def validate_rating(self,value):
        if not 1<=value<=5:
            return serializers.ValidationError('the review have to be >1 & <5')
        return value

    def get_reviews_time(self,obj):
        reviews=Review.objects.filter(user=obj)
        return [{
            'created_at':self.format_datetime(review.created_at),
            'updated_at':self.format_datetime(review.updated_at)}
            for review in reviews]
    
    def format_datetime(self,value):
        return timezone.localtime(value).strftime('%Y-%m-%d %H:%M:%S')
    
class ProductSimpleSerializer(serializers.ModelSerializer):
    save_count=serializers.SerializerMethodField()
    like_count=serializers.SerializerMethodField()
    average_rating=serializers.SerializerMethodField()
    liked=serializers.SerializerMethodField()
    saved=serializers.SerializerMethodField()
    variant_options=serializers.SerializerMethodField()
    # reviews=ReviewSerializer(many=True,read_only=True)
    class Meta:
        model=Product
        fields=["id" , "product_name" , "category",'save_count','average_rating' , "like_count" , "liked" , "saved" , "variant_options"]
    
    def get_save_count(self,obj):
        return obj.save_set.count()
    def get_like_count(self,obj):
        return obj.like_set.count()
    def get_average_rating(self,obj):
        avg = obj.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        return round(avg, 2) if avg else 0
    
    def get_liked(self,obj):
        request = self.context.get('request')
        if request:
            if request.user.is_anonymous:   
                return False
            else:
                return Like.objects.filter(user_id=request.user , product_id=obj).exists()
        else :  
            return False
    def get_saved(self,obj):
        request = self.context.get('request')
        if request:
            if request.user.is_anonymous:   
                return False
            else:
                return Save.objects.filter(user=request.user , product=obj).exists()
        else :
            return False
    def get_variant_options(self, obj):
        variants = obj.variants.all().prefetch_related('options__attribute')
        
        options_dict = {}

        for variant in variants:
            for option  in variant.options.all():
                attr_name = option.attribute.attribute
                option_value = option.option
                unit_qs = option.option_unit_set.all()
                unit_name = unit_qs[0].unit.unit if unit_qs.exists() else ""
                option_value += unit_name
                options_dict.setdefault(attr_name, set()).add(option_value)

        # تحويل المجموعات إلى قوائم
        return {k: list(v) for k, v in options_dict.items()}
        
    
