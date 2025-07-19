from rest_framework import serializers
from .models import *
from employees.models import Employee
from products.serializers import VariantSerializers

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
        
        
     