from rest_framework import serializers
from .models import *
from branches.models import *
from branches.serializers import *
from datetime import date

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
 

class WorkDaySerializer(serializers.ModelSerializer):
    day_name=serializers.CharField(source='get_day_display',read_only=True)
    class Meta:
        model=WorkDay
        fields=['day_name','start_time','end_time','is_working_day']
        extra_kwargs={
            'schedule':{'write_only':True}
        }
    def validate(self,data):
        if data['start_time']>=data['end_time']:
            raise serializers.ValidationError("end time must be after start time")
        return data
    
class WorkScheduleSerializer(serializers.ModelSerializer):
    work_days=WorkDaySerializer(many=True,required=True)
    class Meta:
        model = WorkSchedule
        fields =['id','name','is_active','created_at','updated_at','work_days']
        read_only_fields=['created_at','updated_at']

    def vlidate(self,data):
        if not data.get('work_days'):
            raise serializers.ValidationError('have to add work days')
        days=[day['day'] for day in data['work_days']]
    
    def create(self, validated_data):
        work_days_data=validated_data.pop('work_days')
        schedule=WorkSchedule.objects.create(**validated_data)
        for day_data in work_days_data:
            WorkDay.objects.create(schedule=schedule,**day_data)
        return schedule
    def update(self, instance, validated_data):
        instance.name=validated_data.get('name',instance.name)
        instance.is_active=validated_data.get('is_active',instance.is_active)

        instance.work_days.all().delete()
        work_days_data=validated_data.get('work_days',[])
        for day_data in work_days_data:
            WorkDay.objects.create(schedule=instance,**day_data)
        return instance
    
class AttendanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model=AttendanceLog
        fields=['check_in','check_out']
        read_only_fields=['check_in','check_out']

class AttendanceSerializer(serializers.ModelSerializer):
    logs=AttendanceLogSerializer(read_only=True,many=True)
    class Meta:
        model=Attendance
        fields='__all__'
        read_only_fields=['status','created_at','date','logs']


class VecationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Vecation
        fields=['employee','vecation_type','duration_type','start_date','end_date','created_at']
        read_only_fields=['created_at']

class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model=Salary
        fields=['employee','month','year','base_salary','final_salary','absent_days','unpaid_vecation_days','late_count','generated_at']
        read_only_fields=['salary_list']