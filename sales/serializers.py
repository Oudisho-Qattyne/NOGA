from rest_framework import serializers
from .models import *
from products.serializers import OptionSerializer , ProductSerializer
from products.models import Variant , Product

class DiscountProductOptionSerializer(serializers.ModelSerializer):
    option = OptionSerializer(many=True)
    class Meta:
        model = Discount_Product_Option
        fields = ["id" , "discount_product" , "option"]
    
    # def validate(self, attrs):
    #     validated_data = super().validate(attrs)
    #     discount_product = validated_data.get("discount_product")
    #     option = validated_data.get("option")
    #     variants = Variant.objects.filter(product=discount_product.product.id)
    #     product_has_option = False
    #     for variant in variants:
    #         product_options = variant.options.value_list("id" , flat=True)
    #         if option.id  in product_options:
    #             product_has_option = True
    #             break
    #     if not product_has_option:
    #         raise serializers.ValidationError({"option" : "This product don`t have this option"})

    #     return validated_data

class DiscountProductSerializer(serializers.ModelSerializer):
    options = serializers.PrimaryKeyRelatedField(queryset=Option.objects.all(),many=True , write_only=True, required=False)
    # options = OptionSerializer(many=True)
    class Meta:
        model = Discount_Product
        fields = ["id" , "discount" , "product" , "has_options" , "options" ]
        extra_kwargs={
            "discount":{
                "required":False,
                "write_only":True
            }
        }
    def validate(self, attrs):
        errors = []

        validated_data = super().validate(attrs)
        has_options = validated_data.get("has_options" , None)
        product = validated_data.get("product" , None)
        discount_product_options = validated_data.get('options' , [])

        if has_options:
            if len(discount_product_options) == 0:
                errors.append({'options' : 'This field is required'})
            else:
                variants = Variant.objects.filter(product=product.id)
                for option in discount_product_options:
                    product_has_option = False
                    for variant in variants:
                        product_options = variant.options.values_list("id" , flat=True)
                        if option.id  in product_options:
                            product_has_option = True
                            break
                    if not product_has_option:
                        errors.append({option.id : "This product don`t have this option"})

        if len(errors) !=0:
            raise serializers.ValidationError( {"options" : errors})
        
        return validated_data
    
    
    def create(self, validated_data):
        options = validated_data.pop('options' , [])
        has_options = validated_data.get('has_options' , False)
        discount_product_instance = Discount_Product.objects.create(**validated_data)
        # discount_product_instance = super().create(validated_data)
        if has_options:
            for option in options:
                discount_product_instance.options.add(option)
        return discount_product_instance
    

    def to_representation(self, instance):
        self.fields['options'] = OptionSerializer(many=True, read_only=True)  
        # self.fields['product'] = ProductSerializer(many=True, read_only=True)  
        data = super(DiscountProductSerializer, self).to_representation(instance)
        data['product'] = instance.product.product_name
        return data



class DiscountCategoryOptionSerializer(serializers.ModelSerializer):
    option = OptionSerializer(many=True)
    class Meta:
        model = Discount_Category_Option
        fields = ["id" , "discount_category" , "option"]
    
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        discount_category = validated_data.get("discount_category")
        option = validated_data.get("option")
        products = Product.objects.filter(category= discount_category.category.id)
        category_has_option = False
        for product in products:
            variants = Variant.objects.filter(product=product.product.id)
            for variant in variants:
                product_options = variant.options.value_list("id" , flat=True)
                if option.id  in product_options:
                    category_has_option = True
                    break
        if not category_has_option:
            raise serializers.ValidationError({"option" : "This category don`t have this option"})

        return validated_data

class DiscountCategorySerializer(serializers.ModelSerializer):
    options = serializers.PrimaryKeyRelatedField(queryset=Option.objects.all(),many=True , write_only=True, required=False)
    class Meta:
        model = Discount_Category
        fields = ["id" , "discount" , "category" , "has_options" , "options" ]
        extra_kwargs={
            "discount":{
                "required":False,
                "write_only":True
            }
        }
    def validate(self, attrs):
        errors = []

        validated_data = super().validate(attrs)
        has_options = validated_data.get("has_options" , None)
        category = validated_data.get("category" , None)
        discount_product_options = validated_data.get('options' , [])

        if has_options:
            if len(discount_product_options) == 0:
                errors.append({'options' : 'This field is required'})
            else:
                products = Product.objects.filter(category=category.id)
                for product in products:
                    variants = Variant.objects.filter(product=product.id)
                    for option in discount_product_options:
                        product_has_option = False
                        for variant in variants:
                            product_options = variant.options.values_list("id" , flat=True)
                            if option.id  in product_options:
                                product_has_option = True
                                break
                        if not product_has_option:
                            errors.append({option.id : "This category products don`t have this option"})

        if len(errors) !=0:
            raise serializers.ValidationError( {"options" :errors})
        
        return validated_data
    
    def create(self, validated_data):
        options = validated_data.pop('options' , [])
        has_options = validated_data.get('has_options' , False)
        discount_category_instance = Discount_Category.objects.create(**validated_data)
        # discount_product_instance = super().create(validated_data)
        if has_options:
            for option in options:
                discount_category_instance.options.add(option)
        return discount_category_instance
    

    def to_representation(self, instance):
        self.fields['options'] = OptionSerializer(many=True, read_only=True)  
        # self.fields['product'] = ProductSerializer(many=True, read_only=True)  
        data = super(DiscountCategorySerializer, self).to_representation(instance)
        data['category'] = instance.category.category
        return data

class DiscountSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ["id" , "start_date" , "end_date" , "created_at", "amount" , "discount_type" ]
    

class DiscountSerializer(serializers.ModelSerializer):
    discount_products = DiscountProductSerializer(many=True , required=False)
    discount_categories = DiscountCategorySerializer(many=True , required=False)
    class Meta:
        model = Discount
        fields = ["id" , "start_date" , "end_date" , "created_at", "amount" , "discount_type" , "has_products" , "has_categories" , "for_every_product" , "for_every_product_exept" , "discount_products" , "discount_categories"]
    
    def validate(self, attrs):
        errors = []
        validated_data = super().validate(attrs)
        has_products = validated_data.get("has_products" , False)
        has_categories = validated_data.get("has_categories" , False)
        for_every_product = validated_data.get("for_every_product" , False)
        for_every_product_exept = validated_data.get("for_every_product_exept" , False)
        discount_products = validated_data.get("discount_products" , [])
        discount_categories = validated_data.get("discount_categories" , [])
        if not  for_every_product:
            if not has_categories and not has_products and not for_every_product:
                errors.append({"discount":"Discount has nothing"})
            if has_products and len(discount_products) == 0:
                errors.append({"discount_products":"This field is required"})
            if has_categories and len(discount_categories) == 0:
                errors.append({"discount_categories":"This field is required"})
        

        if len(errors) != 0:
            raise serializers.ValidationError({"discount":errors})

        return validated_data
    

    def create(self, validated_data):

        discount_products = validated_data.pop("discount_products" , [])
        discount_categories = validated_data.pop("discount_categories" , [])
        has_products = validated_data.get("has_products" , False)
        has_categories = validated_data.get("has_categories" , False)
        discount = super().create(validated_data)

        for_every_product = validated_data.get("for_every_product" , False)
        has_products = validated_data.get("has_products" , False)
        has_categories = validated_data.get("has_categories" , False)
        if not for_every_product:
            if has_products:
                for discount_product in discount_products:
                    discount_product['discount'] = discount.id
                    discount_product['product'] = discount_product['product'].id
                    if discount_product['has_options']:
                        discount_product['options'] = list(option.id for option in  discount_product['options'])
                    discount_product_serialized = DiscountProductSerializer(data=discount_product)
                    discount_product_serialized.is_valid(raise_exception=True)
                    discount_product_serialized.save()

            if has_categories:
                for discount_category in discount_categories:
                    discount_category['discount'] = discount.id
                    discount_category['category'] = discount_category['category'].id
                    if discount_category['has_options']:
                        discount_category['options'] = list(option.id for option in  discount_category['options'])
                    discount_category_serialized = DiscountCategorySerializer(data=discount_category)
                    discount_category_serialized.is_valid(raise_exception=True)
                    discount_category_serialized.save()
            
        return discount

    # def update(self, instance, validated_data):
    #     instance = super().update(instance, validated_data)

    #     return 