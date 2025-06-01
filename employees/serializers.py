from rest_framework import serializers
from .models import *
from branches.models import *
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
 