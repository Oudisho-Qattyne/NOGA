from rest_framework import serializers
from .models import *
from branches.models import *
from branches.serializers import *
from datetime import date
from django.utils import timezone
import face_recognition
from .utils import *
from PIL import Image
import io
import cv2
class Job_TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Job_Type
        fields=['id','job_type']
  

class EmployeeSerializer(serializers.ModelSerializer):
    job_type_title=serializers.StringRelatedField(source='job_type')
    branch_name = serializers.SerializerMethodField()
    # address = serializers.SerializerMethodField()
    class Meta:
        model=Employee
        fields=['id' , 'national_number','first_name','middle_name','last_name','email','salary','address','date_of_employment','birth_date','gender','job_type' , 'job_type_title' , 'branch' , 'phone' , 'branch_name' , 'image']
        extra_kwargs = {
            "job_type_title" : {'read_only' : True},
            "job_type" : {
                "required":True
            },
            "branch_name" :{
                "read_only" : True
            },
            "image" :{
                "required" : True
            }
        }
    

    def get_branch_name(self , object):
        if(object.branch):
            return object.branch.city.city_name + " " + str(object.branch.number)
        return 
    # def get_address(self , object):
    #     if(object.branch):
    #         return object.branch.street + ' , ' +  object.branch.area + ' , ' + object.branch.city.city_name
    #     return     
        
        
    def validate(self, attrs):
        validated_data =  super().validate(attrs)
        request= self.context['request']
        image = validated_data.get('image', None)
        if image:
            # قراءة الصورة باستخدام PIL
            try:
                img = Image.open(image)
                img = img.convert('RGB')
                # تحويل الصورة إلى numpy array
                img_array = face_recognition.load_image_file(image)
                # اكتشاف الوجوه في الصورة
                face_locations = face_recognition.face_locations(img_array)
                if len(face_locations) == 0:
                    raise serializers.ValidationError({
                        "image": "No face detected in the uploaded image."
                    })
            except Exception as e:
                raise serializers.ValidationError({
                    "image": "No face detected in the uploaded image."
                })
        if request.method == 'PUT':
            if self.instance.job_type.job_type == "Manager":
                branches = Branch.objects.all()
                relatedBranches = branches.filter(manager= self.instance.id)
                if(len(relatedBranches) > 0 ):
                    raise serializers.ValidationError({'manager' : ['this employee is a manager to a branche , change the manager on this branch then edit this employee']})
        if request.method in ['POST' , "PUT"]:
            date_of_employment = validated_data['date_of_employment']
            birth_date = validated_data['birth_date']
            if date_of_employment < birth_date:
                raise serializers.ValidationError({
                    "date_of_employment":"date of employment can't be before the birth date"
                })
            today = date.today()

            eighteen_years_ago = today.replace(year=today.year - 18)

            if birth_date >= eighteen_years_ago:
                raise serializers.ValidationError({
                    "birth_date":"too young"
                })
        return validated_data
 
    def create(self, validated_data):
        instance = super().create(validated_data)
        image_data = None
        image_rgb = None
        if instance.image and instance.image.path:
            image_bgr = cv2.imread(instance.image.path)
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        if len(image_rgb) > 0 :
            accept_register_new_user(instance.id , image_rgb , 'mediafiles/pickle/')
            print(image_rgb)
        return instance
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        image_data = None
        image_rgb = None
        if instance.image and instance.image.path:
            image_bgr = cv2.imread(instance.image.path)
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        if len(image_rgb) > 0 :
            accept_register_new_user(instance.id , image_rgb , 'mediafiles/pickle/')
            print(image_rgb)
        return instance
class WorkDaySerializer(serializers.ModelSerializer):
    day_name=serializers.CharField(source='get_day_display',read_only=True)
    class Meta:
        model=WorkDay
        fields=['id' , 'day_name','start_time','end_time','is_working_day' , 'day']
        extra_kwargs={
            'schedule':{'write_only':True},
            # 'day':{'write_only':True}
        }
    def validate(self,data):
        if data['start_time']>=data['end_time']:
            raise serializers.ValidationError({"end_time" :"end time must be after start time"})
        return data
    
class WorkScheduleSerializer(serializers.ModelSerializer):
    work_days=WorkDaySerializer(many=True,required=True)
    class Meta:
        model = WorkSchedule
        fields =['id','name','is_active','created_at','updated_at','work_days']
        read_only_fields=['created_at','updated_at']

   
    
    def create(self, validated_data):
        work_days_data=validated_data.pop('work_days')
        is_active=validated_data.get("is_active" , False)
        schedule=WorkSchedule.objects.create(**validated_data)
        for day_data in work_days_data:
            WorkDay.objects.create(schedule=schedule,**day_data)
        if is_active:
            workSchedules = WorkSchedule.objects.exclude(id=schedule.id)
            for workSchedual in workSchedules:
                workSchedual.is_active = False
                workSchedual.save()
        return schedule
    def update(self, instance, validated_data):
        is_active = validated_data.get('is_active',False)
        if instance.is_active == True and is_active == False:
            workSchedule = WorkSchedule.objects.first()
            workSchedule.is_active = True
            workSchedule.save()
        instance.name=validated_data.get('name',instance.name)
        instance.is_active=validated_data.get('is_active',instance.is_active)
        instance.updated_at = timezone.now()  # تعيين تاريخ ووقت التحديث الحالي
        instance.save() 
        instance.work_days.all().delete()
        work_days_data=validated_data.get('work_days',[])
        for day_data in work_days_data:
            WorkDay.objects.create(schedule=instance,**day_data)
        if is_active:
            workSchedules = WorkSchedule.objects.exclude(id=instance.id)
            print(workSchedules)
            for workSchedual in workSchedules:
                workSchedual.is_active = False
                workSchedual.save()
        return instance
    
    
class AttendanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model=AttendanceLog
        fields=['id' ,'check_in','check_out']
        read_only_fields=['check_in','check_out']

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    national_number = serializers.SerializerMethodField()
    logs=AttendanceLogSerializer(read_only=True,many=True)
    class Meta:
        model=Attendance
        fields='__all__'
        read_only_fields=['id' , 'status','created_at','date','logs' ,'check_in_status', 'check_out_status' , "employee_name" , "national_number"]
    def get_employee_name(self , object):
        return object.employee.first_name +" " +  object.employee.middle_name + " " + object.employee.last_name
    def get_national_number(self , object):
        return object.employee.national_number

class VecationSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    national_number = serializers.SerializerMethodField()
    class Meta:
        model=Vecation
        fields=['id' , 'employee' , 'employee_name' , 'national_number' ,'vecation_type','duration_type','start_date','end_date','created_at']
        read_only_fields=['created_at']
    def get_employee_name(self , object):
        return object.employee.first_name +" " +  object.employee.middle_name + " " + object.employee.last_name
    def get_national_number(self , object):
        return object.employee.national_number
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        now = timezone.now().date()  # الحصول على التاريخ الحالي فقط (بدون الوقت)
    
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')
        if start_date >= end_date:
            raise serializers.ValidationError({"end_date" :"end time must be after start time"})
        
        if start_date < now:
            raise serializers.ValidationError({"start_date": "Start date cannot be in the past."})
        if end_date < now:
            raise serializers.ValidationError({"end_date": "End date cannot be in the past."})
        if start_date >= end_date:
            raise serializers.ValidationError({"end_date": "End date must be after start date."})
        
        return validated_data
   
class SalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    national_number = serializers.SerializerMethodField()
    class Meta:
        model=Salary
        fields=['id' , 'employee' , 'employee_name' , 'national_number','month','year','base_salary','final_salary','absent_days','unpaid_vecation_days','late_or_left_early_count','generated_at']
        read_only_fields=['salary_list']
    def get_employee_name(self , object):
        return object.employee.first_name +" " +  object.employee.middle_name + " " + object.employee.last_name
    def get_national_number(self , object):
        return object.employee.national_number