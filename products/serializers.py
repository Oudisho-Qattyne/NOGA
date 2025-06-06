from rest_framework import serializers
from rest_framework.views import Response , status
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
    units = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all(), write_only=True, required=False, many=True) 
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
        has_unit = validated_data.get('has_unit',False)
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
        products = Product.objects.filter(category=instance)
        if(len(products.values_list()) != 0):
            pre_attributes = list(instance.attributes.all().values_list("id" , flat=True))
            new_attributes = list(attr.id for attr in attributes)
            set1 = set(pre_attributes)
            set2 = set(new_attributes)
            if not set1.issubset(set2):
                raise serializers.ValidationError({"error": "Cannot update attributes by removing old ones as there are products associated with the category."})
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

    def update(self, instance, validated_data):
        varients = Varient.objects.filter(product=instance) 
        if(len(varients.values_list()) != 0):
            if instance.category != validated_data['category']:
                raise serializers.ValidationError({"error": "Cannot update category as there are variants associated with the product."})
        return super().update(instance, validated_data)
    

class OptionUnitSerializer(serializers.ModelSerializer):
    unit = UnitSerializer()
    class Meta:
        model = Option_Unit
        fields = ['option' , 'unit']

class OptionSerializer(serializers.ModelSerializer):
    unit = serializers.IntegerField( write_only=True, required=False , allow_null=True ) 
    class Meta:
        model = Option
        fields = ["id" , "option" , "attribute", "unit" ]
        extra_kwargs={
            "id":{
                "read_only" : True
            },
         }
    # def __init__(self,*args,**kwargs):
    #         super(AttributeSerializer,self).__init__(*args, **kwargs)
    #         request=kwargs['context']['request']
    #         if request.method in ["POST","PUT"]:
    #             if 'attribute' in self.initial_data:
    #                 attribute =self.initial_data['attribute']
    #                 attribute_instance = Attribute.objects.get(id = attribute)
    #                 attribute_instance

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        attribute = validated_data['attribute']
        option = validated_data['option']
        if attribute.attribute_type == "string":
            if option.isdigit():
                raise serializers.ValidationError({'option' : ['this option should be string']})
        elif attribute.attribute_type == "number":
            if not option.isdigit():
                raise serializers.ValidationError({'option' : ['this option should be number']})
        print(validated_data)
        if attribute.has_unit:
            unit = validated_data.get('unit' , None)
            if unit == None:
                raise serializers.ValidationError({'unit' : ['this field is required']})
            else:
                attribute_units = list(attribute.units.all().values_list('id' , flat=True))
                if unit not in attribute_units:
                    raise serializers.ValidationError({'unit' : ['wrong unit selected']})

        return validated_data
    def create(self, validated_data):
        unit = validated_data.pop('unit' , None)
        option = super().create(validated_data)
        if unit is not None:
            unit_instance = Unit.objects.get(id=unit)
            option_unit = Option_Unit.objects.create(option=option , unit=unit_instance)
            option_unit.save()
        option.save()
        return option
    
    def to_representation(self, instance):
        # self.fields['attribute'] = AttributeSerializer(read_only=True) 
        data = super(OptionSerializer, self).to_representation(instance) 
        unit = "null"
        if instance.attribute.has_unit:
            unit = Option_Unit.objects.get(option=instance.id).unit.unit
        data['unit'] = unit
        data['attribute'] = instance.attribute.attribute
        return data
    
class VarientSerializers(serializers.ModelSerializer):
    options = OptionSerializer(many=True , required=True)
    class Meta:
        model=Varient
        fields = ["id" , "product" , "quantity" , "wholesale_price" , "selling_price" , "options"]
    
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        attributes = validated_data['product']
        required_product_attributes = list(attributes.category.attributes.all().values_list())
        options = validated_data.get('options' , [])
        product_attributes = list(option['attribute'].id  for option in  options)

        # if len(options) == 0:
        #     missed_attributes = []
        #     for required_attribute in required_product_attributes:
        #     required_attribute_id = required_attribute[0]
        #     if required_attribute_id not in product_attributes:
        #         missed_attributes.append({required_attribute[1] :[f'this option is required']})
        #     attrs = list(attr[1] for attr in required_product_attributes)
        #     raise serializers.ValidationError({"options" :[f'these attributes {attrs} are required']})
        
        missed_attributes = []
        for required_attribute in required_product_attributes:
            required_attribute_id = required_attribute[0]
            if required_attribute_id not in product_attributes:
                missed_attributes.append({required_attribute[1] :[f'this option is required']})
        
        if len(missed_attributes) != 0:
            raise serializers.ValidationError({"options" :missed_attributes})

        option_validation = []
        for option in options:
            data = option
            data['attribute'] = int(option['attribute'].id) 
            option_instance = OptionSerializer(data=data)
            if not option_instance.is_valid():
                option_validation.append({option['attribute'].attribute :[option_instance.errors]})

        if len(option_validation) != 0:
            raise serializers.ValidationError({"options" :option_validation})
        
        return validated_data
    
    def create(self, validated_data):
        options = validated_data.pop("options")
        varient_instance = Varient.objects.create(**validated_data)
        for option in options:
            option_serialized_data = OptionSerializer(data=option)
            option_serialized_data.is_valid(raise_exception=True)
            option_instance =  option_serialized_data.save()
            varient_instance.options.add(option_instance)
        varient_instance.save()
        
        return varient_instance
    
    def update(self, instance, validated_data):
        options = validated_data.pop("options")
        varient_instance = super().update(instance, validated_data)
        instance.options.all().delete()
        for option in options:
            option_serialized_data = OptionSerializer(data=option)
            option_serialized_data.is_valid(raise_exception=True)
            option_instance =  option_serialized_data.save()
            varient_instance.options.add(option_instance)
        # varient_instance.save()
        return varient_instance
   