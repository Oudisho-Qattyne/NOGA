from rest_framework import serializers , exceptions
from .models import *
from mobile.models import Client_Profile
from mobile.serializers import ClientProfileSerializer
from rest_framework_simplejwt.views import TokenObtainPairView 
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer 
from rest_framework_simplejwt.tokens import RefreshToken

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = ["id" , "username" , "password" , 'is_employee' ]
        
        extra_kwargs = {
            "password" : {'write_only' : True},
            'required' : True,
            "id" : {'read_only' : True,
            'required' : True},
            'is_employee':{
                'required':False
            }
        }
    def create(self, validated_data):
        password = validated_data.pop('password' , None)
        user = self.Meta.model(**validated_data)
        if password is not None:
            user.set_password(password)
        user.save()
        return user
    
class EmployeeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=Employee_User
        fields=["user" , "employee"] 

class ClientTokenObtainPairSerializer(TokenObtainPairSerializer):
    token_class = RefreshToken
    def validate(self , attrs):
        data = super().validate(attrs)
        if self.user.is_employee == True:
            raise exceptions.AuthenticationFailed('No active account found with the given credentials')
        refresh = self.get_token(self.user)
        client_profile = Client_Profile.objects.filter(user=self.user).first()
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        if client_profile is not None:
            client_profile_data = ClientProfileSerializer(client_profile)
            data['is_completed'] = True
            data['client_profile'] = client_profile_data.data

        else:
            data['is_completed'] = False
        return data

class EmployeeTokenObtainPairSerializer(TokenObtainPairSerializer):
    token_class = RefreshToken
    
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        if(self.user.is_staff):
            data['role'] = 'admin'
        elif self.user.is_employee == False:
            raise exceptions.AuthenticationFailed('No active account found with the given credentials')
        else:
            data['role'] = self.user.employee_user.employee.job_type.job_type
            if(self.user.employee_user.employee.branch):
                data['branch'] = self.user.employee_user.employee.branch.id
                data['branch_name'] = self.user.employee_user.employee.branch.city.city_name + " " + str(self.user.employee_user.employee.branch.number) 
            if(self.user.employee_user.employee.image):
                data['image'] = f"{self.context.get('request').build_absolute_uri('/')}media/{str(self.user.employee_user.employee.image)}" 
            data['name'] = f"{self.user.employee_user.employee}"
        
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return data
  