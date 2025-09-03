from rest_framework import serializers
from .models import *
from employees.models import Employee
from products.serializers import VariantSerializers
from django.urls import reverse

class BranchSerializer(serializers.ModelSerializer):
    city_name = serializers.StringRelatedField(source='city')
    manager_name = serializers.StringRelatedField(source='manager')
    class Meta:
        model = Branch
        fields = ["id" , "number" , "location" ,"city" , "area" , "street" , "manager" , "city_name" , 'manager_name']
        extra_kwargs = {
         "city" : {
            "required" : True,
            },
         "manager" : {
            "required" : True,
            },
         "number" : {
             "read_only" : True
             },
         "city_name":{
            "read_only" : True
             } ,
         'manager_name' : {
            "read_only" : True
         }
         }
        
    def create(self, validated_data):
        branches = Branch.objects.filter(city=validated_data['city'])
        branchesOrdered = branches.order_by('number')
        branch = self.Meta.model(**validated_data)
        if len(branchesOrdered)>0:
            maxNumber = branchesOrdered[len(branchesOrdered)-1].number 
            branch.number =  maxNumber +  1
        elif len(branchesOrdered)==0:
            print(len(branchesOrdered))
            
            branch.number =  1
        branch.save()
        manager = Employee.objects.get(id = branch.manager.id)
        manager.branch = branch
        manager.save()

        return branch
    
    def validate(self, attrs):
        if(bool(attrs["manager"].job_type.job_type == "Manager")):
            return super().validate(attrs)
        else:
            raise serializers.ValidationError({"manager" : "employee in not manager"})
        
          
        
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id" , "city_name"]
        
class BranchProductsSerializer(serializers.ModelSerializer):
    product = VariantSerializers(read_only=True)
    branch_name = serializers.StringRelatedField(source='branch')

    class Meta:
        model = Branch_Products
        fields = ["id" , "branch" , "product" , "quantity" , "branch_name"]
        
        
class CamerasSerializer(serializers.ModelSerializer):
    branch_name = serializers.SerializerMethodField()
    class Meta:
        model = Camera
        fields = ["id" , "branch" , "branch_name" , "camera_type" , "source_url" , "view_url" , "is_active"]
        extra_kwargs = {
            "source_url":{
                "read_only" : True
            },
            "view_url":{
                "read_only" : True
            } 
        }
    def get_branch_name(self , obj):
        return obj.branch.city.city_name + str(obj.branch.number)
    def create(self, validated_data):
        camera_instance = super().create(validated_data)
        request = self.context.get('request')
        # بناء URL باستخدام reverse وتمرير معرف الكائن
        # url = reverse('camera-detail', kwargs={'pk': camera_instance.pk})
        source_url = request.build_absolute_uri('/ws/source/'+str(camera_instance.id))
        view_url = request.build_absolute_uri('/ws/view/'+str(camera_instance.id))
        source_url = source_url.replace('http://', 'ws://').replace('https://', 'wss://')
        view_url = view_url.replace('http://', 'ws://').replace('https://', 'wss://')
        camera_instance.source_url = source_url
        camera_instance.view_url = view_url
        camera_instance.save()
        return camera_instance

