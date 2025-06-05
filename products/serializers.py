from rest_framework import serializers
from .models import *
from NOGA.utils import *

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model=Unit
        fields=['id' , 'unit']
        extra_kwargs={
            "id":{
                "read_only" : True
            },
        }

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id' , 'attribute' , 'attribute_type' , 'is_multivalue' , 'is_categorical' , 'has_unit' , 'units' ]
        extra_kwargs={
            "id":{
                "read_only" : True
            }
        }

    # def __init__(self,*args,**kwargs):
    #     super(AttributeSerializer,self).__init__(*args, **kwargs)
    #     request=kwargs['context']['request']
    #     if request.method in ["POST","PUT"]:
    #         if 'has_unit' in self.initial_data:
    #             if self.initial_data['has_unit'] == True:
    #                 self.fields['units'].required = True

    def to_representation(self, instance):
        self.fields['units'] = UnitSerializer(many=True, read_only=True)  
        return super(AttributeSerializer, self).to_representation(instance)
    
    def create(self, validated_data):
        units = []
        has_unit = validated_data.pop('has_unit')
        units = validated_data.pop('units')
        attribute = Attribute.objects.create(**validated_data)
        if has_unit:
            for unit in units:
                attribute.units.add(unit)
        return attribute
    def update(self, instance, validated_data):
        units = []
        has_unit = validated_data.get('has_unit' , False)
        units = validated_data.pop('units' , [])
        super().update(instance, validated_data)
        instance.units.clear()
        if has_unit:
            for unit in units:
                instance.units.add(unit)
        else:
            instance.units.clear()
        return instance
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id' , 'category' , 'parent_category' , 'attributes']
        extra_kwargs={
            "id":{
                "read_only" : True
            },
            "parent_category":{
                "required":False
            }
        }
    def create(self, validated_data):
        attributes = validated_data.pop('attributes')
        category = Category.objects.create(**validated_data)
        for attribute in attributes:
            category.attributes.add(attribute)
        return category
    
    def update(self, instance, validated_data):
        attributes = validated_data.pop('attributes' , [])
        super().update(instance, validated_data)
        instance.attributes.clear()
        for attribute in attributes:
            instance.attributes.add(attribute)
        return instance
    
    def to_representation(self, instance):
        self.fields['attributes'] = AttributeSerializer(many=True, read_only=True)  
        return super(CategorySerializer, self).to_representation(instance)
    

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id" , "product_name" , "category" , "qr_code" , "qr_codes_download"]
        extra_kwargs={
            "id":{
                "read_only" : True
            },
            "qr_code":{
                "required":False
            },
            "qr_codes_download":{
                "required":False
            }
        }
    def create(self, validated_data):
        product = Product.objects.create(**validated_data)
        qr_code , qr_codes_download = generateQR(self.context.get('request') , product.id , f'{product.category.category}-{product.product_name}' , product.category.category)
        product.qr_code = qr_code
        product.qr_codes_download = qr_codes_download
        product.save()
        return product
    
    def to_representation(self, instance):
        self.fields['category'] = CategorySerializer(read_only=True)  
        return super(ProductSerializer, self).to_representation(instance)
    
class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["option" , "attribute"]

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        # attribute = validated_data['attribute']
        # option = validated_data['option']
        # if attribute.attribute_type == "string":
        #     if option.isdigit():
        #         raise serializers.ValidationError
        print(validated_data)
        return validated_data
    
    def to_representation(self, instance):
        self.fields['attribute'] = AttributeSerializer(read_only=True)  
        return super(OptionSerializer, self).to_representation(instance)