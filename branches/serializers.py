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
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
    
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
    area_points = serializers.JSONField(required=False, allow_null=True)
    class Meta:
        model = Camera
        fields = ["id" , "branch" , "branch_name" , "camera_type" , "source_url" , "view_url" , "is_active" , "area_points"]
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
        source_url = source_url.replace('http://', 'wss://').replace('https://', 'wss://')
        view_url = view_url.replace('http://', 'wss://').replace('https://', 'wss://')
        camera_instance.source_url = source_url
        camera_instance.view_url = view_url
        camera_instance.save()
        return camera_instance
    
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        area_points = validated_data.get("area_points" , None)
        camera_type = validated_data.get("camera_type" , None)
        if camera_type == "visitors":
            # if area_points is None:
            #     raise serializers.ValidationError({"area_points" : "This field is required"} )
            # else:
            if area_points is not None:
                if not isinstance(area_points, dict):
                    raise serializers.ValidationError("area_points must be a dictionary")

                # يجب أن يحتوي dict على مفاتيح 'area1' و 'area2'
                for key in ['area1', 'area2']:
                    if key not in area_points:
                        raise serializers.ValidationError(f"Missing key '{key}' in area_points")

                    points = area_points[key]
                    if not isinstance(points, list):
                        raise serializers.ValidationError(f"'{key}' must be a list of points")

                    for point in points:
                        if not isinstance(point, dict):
                            raise serializers.ValidationError(f"Each point in '{key}' must be a dict")
                        if 'x' not in point or 'y' not in point:
                            raise serializers.ValidationError(f"Each point in '{key}' must have 'x' and 'y' keys")
                        if not (isinstance(point['x'], (int, float)) and isinstance(point['y'], (int, float))):
                            raise serializers.ValidationError(f"'x' and 'y' must be numbers in '{key}'")

        return validated_data

class BranchVisitorsSerializer(serializers.ModelSerializer):
    branch_name = serializers.SerializerMethodField()
    class Meta:
        model = Branch_Visitors
        fields = ['id', 'branch', 'branch_name' ,  'date', 'visitors_count']
    
    def get_branch_name(self , obj):
        return obj.branch.city.city_name + str(obj.branch.number)