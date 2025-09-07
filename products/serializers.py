from rest_framework import serializers
from rest_framework.views import Response , status
from .models import *
from NOGA.utils import *
from branches.models import Branch_Products
from django.db.models.deletion import ProtectedError

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
    
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
        units = validated_data.pop('units',[])
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
    attributes = serializers.PrimaryKeyRelatedField(queryset=Attribute.objects.all(), write_only=True, required=True, many=True) 

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
        attributes = validated_data.pop('attributes',[])
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
    
class LinkedProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id" , "product_name" , "category"]


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
    #                 if attribute_instance

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        attribute = validated_data['attribute']
        option = validated_data['option']
        if attribute.attribute_type == "string":
            if option.isdigit():
                raise serializers.ValidationError({attribute.attribute : ['this option should be string']})
        elif attribute.attribute_type == "number":
            if not is_float(option):
                raise serializers.ValidationError({attribute.attribute : ['this option should be number']})
        if attribute.has_unit:
            unit = validated_data.get('unit' , None)
            if unit == None:
                raise serializers.ValidationError({attribute.attribute : ['unit field is required']})
            else:
                attribute_units = list(attribute.units.all().values_list('id' , flat=True))
                if unit not in attribute_units:
                    raise serializers.ValidationError({attribute.attribute : ['wrong unit selected']})

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
    
    def update(self, instance, validated_data):
        unit = validated_data.pop('unit' , None)
        super().update(instance, validated_data)
        if unit is not None:
            unit_instance = Unit.objects.get(id=unit)
            try:
                option_unit =  Option_Unit.objects.filter(option=instance , unit = unit_instance)[0]
                option_unit.unit = unit_instance
                option_unit.save()
            except Option_Unit.DoesNotExist:
                option_unit = Option_Unit.objects.create(option=instance , unit=unit_instance)
                option_unit.save()
        else:
            try:
                Option_Unit.objects.filter(option=instance , unit = unit_instance).delete()
            except Option_Unit.DoesNotExist:
                pass
        return instance
    
    def to_representation(self, instance):
        # self.fields['attribute'] = AttributeSerializer(read_only=True) 
        data = super(OptionSerializer, self).to_representation(instance) 
        unit = "null"
        if instance.attribute.has_unit:
            try :
                unit = Option_Unit.objects.get(option=instance.id).unit.unit
            except Option_Unit.DoesNotExist:
                unit = "null"
        data['unit'] = unit
        data['attribute'] = instance.attribute.attribute
        return data

class VariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant_Image
        fields = ['id', 'image']


class VariantSerializers(serializers.ModelSerializer):
    options = OptionSerializer(many=True , required=True)
    discount = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    images = VariantImageSerializer(many = True  , required = False)
    class Meta:
        model=Variant
        fields = ["id" , "product" , "quantity" , "wholesale_price" , "selling_price" , "options" , "sku" , "discount" , "total" , "qr_code" , "qr_codes_download" , "images"]
        extra_kwargs={
            "sku":{
                "read_only":True
            }
        }
    def validate(self, attrs):
        options = attrs.get('options' , [])
        validated_data = super().validate(attrs)
        attributes = validated_data['product']
        required_product_attributes = list(attributes.category.attributes.all().values_list())
        required_product_attributes_ids = list(required_product_attribute[0]  for required_product_attribute in  required_product_attributes)

        # if len(options) == 0:
        #     missed_attributes = []
        #     for required_attribute in required_product_attributes:
        #     required_attribute_id = required_attribute[0]
        #     if required_attribute_id not in product_attributes:
        #         missed_attributes.append({required_attribute[1] :[f'this option is required']})
        #     attrs = list(attr[1] for attr in required_product_attributes)
        #     raise serializers.ValidationError({"options" :[f'these attributes {attrs} are required']})
        attributes_errors = []

        needed_options = []
        for option in options:
            if option['attribute'].id  in required_product_attributes_ids:
                needed_options.append(option)

        options = needed_options

        # check for missing attributes
        product_attributes = list(option['attribute'].id  for option in  options)
        for required_attribute in required_product_attributes:
            required_attribute_id = required_attribute[0]
            if required_attribute_id not in product_attributes:
                attributes_errors.append({required_attribute[1] :[f'this option is required']})
        
        # check for multivalue attributes
        repeated_attributes = list(set([option['attribute'] for option in options if product_attributes.count(option['attribute'].id) > 1]))
        for repeated_attribute in repeated_attributes:
            if not repeated_attribute.is_multivalue:
                attributes_errors.append({repeated_attribute.attribute :[f'this attribute is not multivalue']})

       

        for option in options:
            data = option
            data['attribute'] = int(option['attribute'].id) 
            option_instance = OptionSerializer(data=data)
            if not option_instance.is_valid():
                attributes_errors.append({"options" :[option_instance.errors]})

        if len(attributes_errors) != 0:
            raise serializers.ValidationError({"options" :attributes_errors})
        
        validated_data['options'] = options
        return validated_data
    
    def create(self, validated_data):
        options = validated_data.pop("options")
        images_data = self.context['request'].FILES.getlist('images')
        variant_instance = Variant.objects.create(**validated_data)

        for option in options:
            option_instance = None
            attribute = Attribute.objects.get(id=option['attribute'])
            if attribute.is_categorical:
                option_instances = Option.objects.filter(option=option['option'] , attribute=option['attribute'] , option_unit__unit=option['unit'])
                if(len(option_instances)>1):
                    option_instance = option_instances[0]
                else:
                    option_serialized_data = OptionSerializer(data=option)
                    option_serialized_data.is_valid(raise_exception=True)

                    option_instance =  option_serialized_data.save()
            else:
                option_serialized_data = OptionSerializer(data=option)
                option_serialized_data.is_valid(raise_exception=True)
                option_instance =  option_serialized_data.save()
            variant_instance.options.add(option_instance)
        variant_instance.sku = generate_sku(variant_instance.product.product_name, variant_instance.options)
        qr_code , qr_codes_download = generateQR(self.context.get('request') , variant_instance.id , f'{variant_instance.product.category.category}-{variant_instance.product.product_name}-{variant_instance.sku}' , variant_instance.product.category.category)
        variant_instance.qr_code = qr_code
        variant_instance.qr_codes_download = qr_codes_download
        for image_data in images_data:
            Variant_Image.objects.create(variant=variant_instance, image=image_data)
        variant_instance.save()
        
        return variant_instance
    
    def update(self, instance, validated_data):
        options = validated_data.pop("options")
        images_data = self.context['request'].FILES.getlist('images')

        variant_instance = super().update(instance, validated_data)
        # instance.options.filter(attribute__is_categorical=False).delete()
        instance.options.clear()
        for option in options:
            option_instance = None
            attribute = Attribute.objects.get(id=option['attribute'])
            if attribute.is_categorical:
                option_instances = Option.objects.filter(option=option['option'] , attribute=option['attribute'] , option_unit__unit=option['unit'])
                if(len(option_instances)>1):
                    option_instance = option_instances[0]
                else:
                    option_serialized_data = OptionSerializer(data=option)
                    option_serialized_data.is_valid(raise_exception=True)
                    option_instance =  option_serialized_data.save()
            else:
                option_serialized_data = OptionSerializer(data=option)
                option_serialized_data.is_valid(raise_exception=True)
                option_instance =  option_serialized_data.save()
            variant_instance.options.add(option_instance)
        # variant_instance.save()
        variant_instance.sku = generate_sku(variant_instance.product.product_name, variant_instance.options)
        qr_code , qr_codes_download = generateQR(self.context.get('request') , variant_instance.id , f'{variant_instance.product.category.category}-{variant_instance.product.product_name}-{variant_instance.sku}' , variant_instance.product.category.category)
        variant_instance.qr_code = qr_code
        variant_instance.qr_codes_download = qr_codes_download
        if images_data:
            variant_instance.images.all().delete()
        for image_data in images_data:
            Variant_Image.objects.create(variant=variant_instance, image=image_data)
        return variant_instance

    def get_discount(self,variant):
        data = calculate_discount(self , variant)
        return data['discount']

    def get_total(self,variant):
        data = calculate_discount(self , variant)
        return data['total']
    
    def to_representation(self, instance):
        # self.fields['product'] = ProductSerializer(read_only=True) 
        data = super(VariantSerializers, self).to_representation(instance) 
        data['product'] = instance.product.product_name
        data['category'] = instance.product.category.category
        data['main_product'] = instance.product.id
        return data

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_Image
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    linked_products = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all() , many=True , required=False )
    variants = VariantSerializers(many=True , required=False , read_only=True)
    images = ProductImageSerializer(many=True  , required=False)
    class Meta:
        model = Product
        fields = ["id" , "product_name" , "category" , "qr_code" , "qr_codes_download" , "linked_products" , "variants" , "images"]
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
        linked_products = validated_data.pop('linked_products' , [])
        images_data = self.context['request'].FILES.getlist('images')
        product = Product.objects.create(**validated_data)
        qr_code , qr_codes_download = generateQR(self.context.get('request') , product.id , f'{product.category.category}-{product.product_name}' , product.category.category)
        product.qr_code = qr_code
        product.qr_codes_download = qr_codes_download
        for linked_product in linked_products:
            product.linked_products.add(linked_product)
        for image_data in images_data:
            Product_Image.objects.create(product=product, image=image_data)
        product.save()
        return product
    
    def to_representation(self, instance):
        self.fields['category'] = CategorySerializer(read_only=True)  
        self.fields['linked_products'] = LinkedProductsSerializer(read_only=True , many=True)  
        return super(ProductSerializer, self).to_representation(instance)

    def update(self, instance, validated_data):
        images_data = self.context['request'].FILES.getlist('images')

        if images_data:
            instance.images.all().delete()
            for image_data in images_data:
                Product_Image.objects.create(product=instance, image=image_data)
        variants = Variant.objects.filter(product=instance) 
        if(len(variants.values_list()) != 0):
            if instance.category != validated_data['category']:
                raise serializers.ValidationError({"error": "Cannot update category as there are variants associated with the product."})
        return super().update(instance, validated_data)
    



class TransportedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transported_Products
        fields = ["id" , "transportation" , "product" , 'quantity' ]
        extra_kwargs={
            "transportation":{
                "required":False,
                "write_only":True
            }
        }
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        transportation = attrs.get('transportation',None) or self.context.get('transportation',None)
        variant = validated_data['product']
        quantity = validated_data['quantity']
        # transportation = validated_data['transportation']
        if transportation is not None:
            if transportation.source != None:
                try:
                    variant = Branch_Products.objects.get(branch=transportation.source ,product=variant.id) 
                except Branch_Products.DoesNotExist:
                    raise serializers.ValidationError({variant.product.product.product_name : "This product does not exist in this branch"})
        if variant.quantity < quantity:
            if transportation is not None:
                if transportation.source != None:
                    raise serializers.ValidationError({variant.product.product.product_name : "The amount transported greater than you have"})
                else :
                    raise serializers.ValidationError({variant.product.product_name : "The amount transported greater than you have"})
        return validated_data

    def to_representation(self, instance):
        self.fields['product'] = VariantSerializers(read_only=True) 
        data = super(TransportedProductSerializer, self).to_representation(instance) 
        # data['product'] = instance.product.product.product_name
        return data
    
class ReceivedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Received_Products
        fields = ["id" , "transportation" , "product" , 'quantity']
        extra_kwargs={
            "transportation":{
                "required":False,
                "write_only":True
            }
        }
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        transportation = validated_data['transportation']
        transported_products = transportation.transported_products
        ids = list(x.product.id for x in transported_products)
        variant = validated_data['product']
        quantity = validated_data['quantity']
        if variant.id not in ids:
            raise serializers.ValidationError({variant.product.product_name : "This product is not transported"})
        transported_product = find_element_by_id(transported_products , variant.id)
        
        

        if transported_product.quantity < quantity:
            raise serializers.ValidationError({variant.product.product_name : "The amount received greater than transported"})
        
        return validated_data

    def to_representation(self, instance):
        self.fields['product'] = VariantSerializers(read_only=True) 
        data = super(ReceivedProductSerializer, self).to_representation(instance) 
        return data
    
class TransportationSerializer(serializers.ModelSerializer):
    transported_products = TransportedProductSerializer(many=True)
    received_products = ReceivedProductSerializer(many=True , required=False)
    class Meta:
        model = Transportation
        fields = ["id" , "transportation_status" , "source" , "destination" , "code" , "transported_products" , "received_products" , "created_at" , "transported_at" , "received_at"]
        extra_kwargs={
            "id":{
                "read_only" : True
            },
            "source":{
                "required":False
            },
            "code":{
                "required":False
            },
            "destination" : {
                "required":False,
                "read_only" : False
            },
            "received_products":{
                "read_only":True,
                "required":False,

            },
            "created_at":{
                "required":False,
                "read_only":True
            }
        }
    def validate(self, attrs):
        errors = []
        validated_data = super().validate(attrs)
        transported_products = validated_data.get('transported_products',[])
        source = validated_data.get('source',None)
        for transported_product in transported_products:
            variant_instance = transported_product['product']
            quantity = transported_product['quantity']
            if source != None:
                try:
                    variant_instance = Branch_Products.objects.get(branch=source ,product=variant_instance.id) 
                    if variant_instance.quantity < quantity:
                            errors.append({variant_instance.product.product.product_name : "The amount transported greater than you have"})
                except Branch_Products.DoesNotExist:
                    errors.append({variant_instance.product.product_name : "This product does not exist in this branch"}) 
            else:
                if variant_instance.quantity < quantity:
                        errors.append({variant_instance.product.product_name : "The amount transported greater than you have"})


        if len(errors) > 0:
            raise serializers.ValidationError({"transported_products" : errors})
        return validated_data
    def create(self, validated_data):
        transported_products = validated_data.pop('transported_products',[])
        transportation = super().create(validated_data)

        for transported_product in transported_products:
            variant_instance = transported_product['product']
            if transportation.source != None:
                variant_instance = Branch_Products.objects.get(branch=transportation.source ,product=variant_instance.id) 

            transported_product['product'] = transported_product['product'].id
            transported_product['transportation'] = transportation.id
            transported_product_serialized = TransportedProductSerializer(data=transported_product , context={'transportation': transportation})
            transported_product_serialized.is_valid(raise_exception=True)
            # variant_instance = Variant.objects.get(id=transported_product.id)
            transported_product_serialized.save()
            variant_instance.quantity = variant_instance.quantity - transported_product['quantity']
            variant_instance.save()
        transportation.save()
        return transportation
    # def to_representation(self, instance):
    #     self.fields['transported_products'] = TransportedProductSerializer(read_only=True)  
    #     return super(TransportationSerializer, self).to_representation(instance)
    def update(self, instance, validated_data):
        if instance.transportation_status == 'packaging':
            transported_products = validated_data.pop('transported_products',[])
            transportation_instance = super().update(instance, validated_data)
            #return old transported products 
            old_transported_products = Transported_Products.objects.filter(transportation = instance)
            for old_transported_product in old_transported_products:
                variant_instance = old_transported_product.product
                if instance.source != None:
                    variant_instance = Branch_Products.objects.get(branch=instance.source ,product=variant_instance.id) 
                variant_instance.quantity = variant_instance.quantity + old_transported_product.quantity
                old_transported_product.delete()
                variant_instance.save()
            
            for transported_product in transported_products:
                variant_instance2 = transported_product['product']
                if transportation_instance.source != None:
                    variant_instance2 = Branch_Products.objects.get(branch=transportation_instance.source ,product=variant_instance.id) 

                transported_product['product'] = transported_product['product'].id
                transported_product['transportation'] = transportation_instance.id
                transported_product_serialized = TransportedProductSerializer(data=transported_product)
                transported_product_serialized.is_valid(raise_exception=True)
                transported_product_serialized.save()
                variant_instance2.quantity = variant_instance.quantity - transported_product['quantity']
                variant_instance2.save()     
            transportation_instance.save()

            # check for produt requests for this transportation
            transport_request_instances = Transport_Request.objects.filter(transportation = transportation_instance)
            for transport_request in transport_request_instances:
                requested_products_instances = transport_request.requested_products
                 # transported_products_ids = list(product['product'] for product in transported_products)

                is_fully_approved = True
                is_rejected = True
                for requested_product in requested_products_instances:
                    transported_product = find_element_by_id2(transported_products , requested_product.product.id )
                    if transported_product is not None:
                        if transported_product['quantity'] >= requested_product.quantity:
                            requested_product.product_request_status = "fully-approved"
                            is_rejected = False
                        else:
                            requested_product.product_request_status = "partially-approved"
                            is_fully_approved = False
                            is_rejected = False
                    else:
                        requested_product.product_request_status = "rejected"
                        is_fully_approved = False
                    requested_product.save()
                if is_fully_approved:
                    transport_request.request_status = "fully-approved"
                elif is_rejected:
                    transport_request.request_status = "rejected"
                else:
                    transport_request.request_status = "partially-approved"
                transport_request.transportation = transportation_instance
                transport_request.save()
            return transportation_instance
        else:
            raise serializers.ValidationError({'message' : 'The transfer cannot be updated after it has been sent.'})
    
    def to_representation(self, instance):
        from branches.serializers import BranchSerializer
        self.fields['source'] = BranchSerializer(read_only=True) 
        self.fields['destination'] = BranchSerializer(read_only=True) 
        data = super(TransportationSerializer, self).to_representation(instance) 
        if instance.source:
            data['source'] = instance.source.city.city_name + str(instance.source.number)
        if instance.destination:
            data['destination'] = instance.destination.city.city_name + str(instance.destination.number)
        return data
class RequestedProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requested_Products
        fields =["id" , "request" , "product_request_status" , "product" , "quantity"]
        extra_kwargs={
            "request":{
                "required":False,
                "write_only":True
            },
            "request_status":{
                "read_only":True
            }
        }
    def to_representation(self, instance):
        self.fields['product'] = VariantSerializers(read_only=True) 
        data = super(RequestedProductsSerializer, self).to_representation(instance) 
        return data
class TransportRequestSerializer(serializers.ModelSerializer):
    requested_products = RequestedProductsSerializer(many=True)
    transportation = TransportationSerializer(required = False)
    class Meta:
        model = Transport_Request
        fields = ["id" , "request_status" , "branch" , "requested_products" , "transportation" , "created_at"]
        extra_kwargs = {
            "transportation":{
                "read_only":True,
                "required":False
            },
            "created_at":{
                "required":False,
                "read_only":True
            }
        }
    def to_representation(self, instance):
        data = super(TransportRequestSerializer, self).to_representation(instance) 
        data['branch_name'] = instance.branch.city.city_name + str(instance.branch.number)
        return data
    def create(self, validated_data):
        requested_products = validated_data.pop("requested_products" , [])
        transport_request_instance = super().create(validated_data)
        for requested_product in requested_products:
            requested_product['request'] = transport_request_instance.id
            requested_product['product'] = requested_product['product'].id
            requested_product_serialized_data = RequestedProductsSerializer(data=requested_product)
            requested_product_serialized_data.is_valid(raise_exception=True)
            requested_product_instance = requested_product_serialized_data.save()
        transport_request_instance.save()
        return transport_request_instance
    
    def update(self, instance, validated_data):
        if instance.request_status == 'waiting':
            requested_products = validated_data.pop('requested_products',[])
            transport_request_instance = super().update(instance, validated_data)
            Requested_Products.objects.filter(request = transport_request_instance).delete()
            for requested_product in requested_products:
                requested_product['product'] = requested_product['product'].id
                requested_product['request'] =  transport_request_instance.id
                requested_product_serialized = RequestedProductsSerializer(data=requested_product)
                requested_product_serialized.is_valid(raise_exception=True)
                requested_product_serialized.save()
            transport_request_instance.save()
            return transport_request_instance
        else:
            raise serializers.ValidationError({'message' : 'The request cannot be updated after it has been processed.'})


class RecommendationSerializer(serializers.Serializer):
    product = ProductSerializer()
    score = serializers.FloatField()
    reason = serializers.CharField()
