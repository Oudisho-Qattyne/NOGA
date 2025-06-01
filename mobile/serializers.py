from rest_framework import serializers
from .models import *

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