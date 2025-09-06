from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from rest_framework import status , generics
from .models import *
from rest_framework import exceptions
from .authentication import *
from mobile.models import Client_Profile
from mobile.serializers import ClientProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.contrib import messages
# Create your views here.

class ClientRrgisterAPIView(APIView):
    def post(self , requset):
        data = requset.data
       
        if(data["password"] != data["confirm_password"]):
            return Response({
                "validationError" : "password and confirm_password don't macth",
            })
        requset.data['is_employee'] = False
        domain = f"{requset.scheme}://{requset.get_host()}"
        serializedData = UserSerializer(data=requset.data , context={'domain': domain})
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
        emp = Employee.objects.get(id=employee)
        requset.data['email'] = str(emp.national_number) + "@noga.com"
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
        


class VerifyEmailAPIView(APIView):
    def get(self, request, token):
        try:
            user = User.objects.get(email_verification_token=token)
            user.is_email_verified = True
            user.is_active = True
            user.email_verification_token = ''
            user.save()
            message = "Email verified successfully."
            return render(request, 'emailverificationresult.html', {'message': message, 'success': True}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            message = "Invalid token."
            return render(request, 'emailverificationresult.html', {'message': message, 'success': False}, status=status.HTTP_400_BAD_REQUEST)
        

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


class PasswordResetRequestAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        token = token_generator.make_token(user)
        domain = f"{request.scheme}://{request.get_host()}"
        reset_link = f"{domain}/reset-password-confirm/{user.pk}/{token}/"
        
        send_mail(
            subject="Password Reset Request",
            message=f"To reset your password, click the following link: {reset_link}",
            from_email="noreply@yourdomain.com",
            recipient_list=[email],
            fail_silently=False,
        )
        
        return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)
    
def password_reset_confirm(request, uid, token):
    try:
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        user = None

    if user is None or not token_generator.check_token(user, token):
        messages.error(request, "الرابط غير صالح أو منتهي الصلاحية.")
        return redirect('password_reset_invalid')

    if request.method == 'POST':
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password and password == password2:
            user.set_password(password)
            user.save()
            messages.success(request, "تم إعادة تعيين كلمة المرور بنجاح!")
            return redirect('password_set')  # أو أي صفحة تريد إعادة التوجيه إليها
        else:
            messages.error(request, "كلمتا المرور غير متطابقتين.")

    return render(request, 'password_reset_confirm.html', {'uid': uid, 'token': token})

def password_reset_invalid(request):
   
    return render(request, 'password_reset_invalid.html')

def password_set(request):
   
    return render(request, 'password_set.html')

class DeleteUserAndProfileAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        # السماح فقط للمستخدم الحالي بحذف حسابه
        return self.request.user

    def perform_destroy(self, instance):
        # حذف Client_Profile المرتبط أولاً
        try:
            profile = Client_Profile.objects.get(user=instance)
            profile.delete()
        except Client_Profile.DoesNotExist:
            pass
        # ثم حذف المستخدم
        instance.delete()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "User and client profile deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

