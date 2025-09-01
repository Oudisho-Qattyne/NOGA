from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from rest_framework import status
from .models import *
from rest_framework import exceptions
from .authentication import *
from mobile.models import Client_Profile
from mobile.serializers import ClientProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
# Create your views here.

class ClientRrgisterAPIView(APIView):
    def post(self , requset):
        data = requset.data
       
        if(data["password"] != data["confirm_password"]):
            return Response({
                "validationError" : "password and confirm_password don't macth",
            })
        requset.data['is_employee'] = False
        serializedData = UserSerializer(data=requset.data)
        serializedData.is_valid(raise_exception=True)
        serializedData.save()
        
        return Response(serializedData.data , status=status.HTTP_200_OK)
    
class EmployeeRrgisterAPIView(APIView):
    def post(self , requset):
        data = requset.data
        employee = data["employee"]
        if(employee == None):
            return Response({
               "employee": [
                "This field is required."
                ]
            })
        if(data["password"] != data["confirm_password"]):
            return Response({
                "validationError" : "password and confirm_password don't macth",
            })
        try:
            emp = Employee.objects.get(id=employee)
        except Employee.DoesNotExist:
            return Response({
               "employee": [
                "This employee does not exist."
                ]
            } , status=status.HTTP_404_NOT_FOUND)
        employee_exists = Employee_User.objects.filter(employee=employee).exists()
        if(employee_exists == True):
            return Response({
               "employee": [
                "This employee already has user."
                ]
            } , status=status.HTTP_403_FORBIDDEN)
        requset.data['is_employee'] = True
        serializedData = UserSerializer(data=requset.data)
        serializedData.is_valid(raise_exception=True)
        user = serializedData.save()
        serializedData2 = EmployeeUserSerializer(data={"user":user.id,"employee":emp.id})
        serializedData2.is_valid(raise_exception=True)
        serializedData2.save()
        
        return Response(serializedData.data , status=status.HTTP_200_OK)
 
# class ClientLoginAPIView(APIView):
#     def post(self , requset):
#         username = requset.data['username']
#         password = requset.data['password']

#         user = User.objects.filter(username = username).first()

#         if user is None or user.is_employee == True:
#             raise exceptions.AuthenticationFailed('Invalid credentials')
#         if not user.check_password(password):
#             raise exceptions.AuthenticationFailed('Invalid credentials')
#         access_token = create_access_token(user.id)
#         refresh_token = create_refresh_token(user.id)
#         client_profile = Client_Profile.objects.filter(user = user).first()
        

#         res = Response()

#         res.data = {
#         "access_token" : access_token,
#         "refresh_token" : refresh_token
#         }
#         if client_profile is not None:
#             serializedClientProfile = ClientProfileSerializer(client_profile)
#             res.data['client_profile'] = serializedClientProfile
#             res.data['is_completed'] = True

#         else:
#             res.data['is_completed'] = False
#         return res
    
class ClientTokenObtainPairView(TokenObtainPairView):
    serializer_class=ClientTokenObtainPairSerializer
  
class EmployeeTokenObtainPairView(TokenObtainPairView):
    serializer_class=EmployeeTokenObtainPairSerializer
  
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        refresh_token = request.data.get("refresh", None)
        if not refresh_token:
            return Response({"refresh": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"detail": "Token is invalid or expired"}, status=status.HTTP_400_BAD_REQUEST)