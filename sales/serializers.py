from rest_framework import serializers
from .models import *
from products.serializers import OptionSerializer , ProductSerializer
from products.models import Variant , Product
from NOGA.utils import calculate_discount_instance , check_options , is_valid_offer
from branches.models import Branch_Products
import copy
from django.forms.models import model_to_dict

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


class OfferProductOptionSerializer(serializers.ModelSerializer):
    option = OptionSerializer(many=True)
    class Meta:
        model = Offer_Product_Option
        fields = ["id" , "Offer_product" , "option"]
    

class OfferProductSerializer(serializers.ModelSerializer):
    options = serializers.PrimaryKeyRelatedField(queryset=Option.objects.all(),many=True , write_only=True, required=False)
    # options = OptionSerializer(many=True)
    class Meta:
        model = Offer_Product
        fields = ["id" , "offer" , "product" , "has_options" , "options" , "quantity"]
        extra_kwargs={
            "offer":{
                "required":False,
                "write_only":True
            }
        }
    def validate(self, attrs):
        errors = []

        validated_data = super().validate(attrs)
        has_options = validated_data.get("has_options" , None)
        product = validated_data.get("product" , None)
        offer_product_options = validated_data.get('options' , [])

        if has_options:
            if len(offer_product_options) == 0:
                errors.append({'options' : 'This field is required'})
            else:
                variants = Variant.objects.filter(product=product.id)
                for option in offer_product_options:
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
        offer_product_instance = Offer_Product.objects.create(**validated_data)
        # offer_product_instance = super().create(validated_data)
        if has_options:
            for option in options:
                offer_product_instance.options.add(option)
        return offer_product_instance
    

    def to_representation(self, instance):
        self.fields['options'] = OptionSerializer(many=True, read_only=True)  
        # self.fields['product'] = ProductSerializer(many=True, read_only=True)  
        data = super(OfferProductSerializer, self).to_representation(instance)
        data['product'] = instance.product.product_name
        return data


class OfferSerializer(serializers.ModelSerializer):
    offer_products = OfferProductSerializer(many=True , required=False)
    # discount_categories = DiscountCategorySerializer(many=True , required=False)
    class Meta:
        model = Offer
        fields = ["id" , "start_date" , "end_date" , "created_at", "price" , "offer_products" ]
    
    def validate(self, attrs):
        errors = []
        validated_data = super().validate(attrs)
        offer_products = validated_data.get("offer_products" , [])

        if  len(offer_products) == 0:
            errors.append({"offer_products":"This field is required"})
        

        if len(errors) != 0:
            raise serializers.ValidationError({"offer":errors})

        return validated_data
    

    def create(self, validated_data):

        offer_products = validated_data.pop("offer_products" , [])
        offer = super().create(validated_data)
        for offer_product in offer_products:
            offer_product['offer'] = offer.id
            offer_product['product'] = offer_product['product'].id
            if offer_product['has_options']:
                offer_product['options'] = list(option.id for option in  offer_product['options'])
            offer_product_serialized = OfferProductSerializer(data=offer_product)
            offer_product_serialized.is_valid(raise_exception=True)
            offer_product_serialized.save()
            
        return offer


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id' , "code" , "start_date" , "end_date" , "created_at" , "amount" , "discount_type" , "min_price" , "max_price" , "quantity"]

class PurchasedProductsSerializer(serializers.ModelSerializer):
    discount = serializers.PrimaryKeyRelatedField(queryset=Discount.objects.all() , write_only=True, required=False)
    offer = serializers.PrimaryKeyRelatedField(queryset=Offer.objects.all() , write_only=True, required=False)
    class Meta:
        model = Purchased_Products
        fields = ["id" , "purchase" , "product" , "wholesale_price" , "selling_price" , "total_price" , "has_discount"  , "discount" , "in_pack" , "offer"  , "quantity"]
        extra_kwargs={
            "wholesale_price":{
                "required":False,
                # "write_only":True
            },
            "selling_price":{
                "required":False,
                # "write_only":True
            },
            "offer":{
                "required":False,
            },
            "has_discount":{
                "required":False
            },
            "in_pack":{
                "required":False
            },
            "total_price":{
                "required":False
            },
            "offer":{
                "required":False,
            },
            "discont":{
                "required":False,
                "read_only":True
            },
             "purchase":{
                "required":False,
            },
        }
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        in_pack = validated_data.get("in_pack" , False)
        offer = validated_data.get("offer" , None)
        product = validated_data.get("product" , None)
        quantity = validated_data.get("quantity" , None)
        if in_pack == True and offer is None:
            raise serializers.ValidationError({product.product.product_name : "Offer is required"})
        
        if in_pack == True and offer is not None:
            if is_valid_offer(offer):
                op = [offer_product for offer_product in offer.offer_products if offer_product.product.id == product.product.id]
                if len(op) > 0:
                    op = op[0]
                    if op.has_options:
                        op_options = set(option for option in op.options.all() )
                        variant_options = set(option for option in product.options.all())
                        if not check_options(variant_options , op_options):
                            raise serializers.ValidationError({"offer" : "This offer does not include this product."})
                        else:
                            print(quantity)
                            print(op.quantity)
                            if quantity > op.quantity:
                                raise serializers.ValidationError({"offer" : "This offer does not include this amount of product."})
                    if quantity > op.quantity:
                                raise serializers.ValidationError({"offer" : "This offer does not include this amount of product."})

                else:
                    raise serializers.ValidationError({"offer" : "This offer does not include this product."})
            else:
                    raise serializers.ValidationError({"offer" : "This offer is not valid."})
        return validated_data  
    
    def create(self, validated_data):
        # offer = validated_data.get("offer" , None)
        # if offer is not None:
            # validated_data["offer"] = offer.id
        purchased_product =  super().create(validated_data)
        
        return purchased_product
    
    def to_representation(self, instance):
        self.fields['discount'] = DiscountSimpleSerializer( read_only=True)  
        self.fields['offer'] = OfferSerializer( read_only=True)  
        # self.fields['product'] = ProductSerializer(many=True, read_only=True)  
        data = super(PurchasedProductsSerializer, self).to_representation(instance)
        # data['product'] = instance.product.product_name
        return data
    
class PurchaseSerializer(serializers.ModelSerializer):
    purchased_products = PurchasedProductsSerializer(many=True)
    purchased_offers = serializers.PrimaryKeyRelatedField(queryset=Offer.objects.all() , write_only=True, required=False , many = True)
    class Meta:
        model = Purchase
        fields = ["id" , "branch" , "customer" , "status" , "date_of_purchase" , "created_at" , "subtotal_price" ,"total_price" , "has_coupons" , "coupon" , "purchased_products" ,"purchased_offers"]
        extra_kwargs={
            "coupon":{
                "required":False,
            },
            "has_coupon":{
                "required":False,
            },
            "total_price":{
                "required":False,
            },
            "subtotal_price":{
                "required":False,
            },
        }
    def validate(self, attrs):
        errors = {}
        purchased_products_errors = []

        validated_data = super().validate(attrs)
        purchased_products = validated_data.get("purchased_products" , None)
        purchased_offers = validated_data.get("purchased_offers" , [])

        if len(purchased_offers) > 0 :
            validated_data['has_offers'] = True
        if purchased_products is None:
            errors["purchased_products"] = "This field is required"
        if len(purchased_products) <= 0 :
            errors["purchased_products"] = "This field is required"
        products_in_pack = {}
        products = {}
        all_products = {}
        if len(purchased_offers) > 0:
            # products_in_pack = {product for product in purchased_product.items() if product["in_pack"] == True}
            for purchased_product in purchased_products:
                in_pack = purchased_product.get("in_pack" , False)
                if purchased_product["product"].product.id in all_products:
                    all_products[purchased_product["product"].id]["quantity"] += purchased_product["quantity"]
                else :
                    all_products[purchased_product["product"].id] = purchased_product
                if in_pack == True:
                    if purchased_product["product"].product.id in products_in_pack:
                        products_in_pack[purchased_product["product"].id]["quantity"] += purchased_product["quantity"]
                    else :
                        products_in_pack[purchased_product["product"].id] = purchased_product
                else:
                    if purchased_product["product"].product.id in products:
                        products[purchased_product["product"].id]["quantity"] += purchased_product["quantity"]
                    else :
                        products[purchased_product["product"].id] = purchased_product
        purchased_offers_errors = []
        products_in_pack_temp = copy.deepcopy(products_in_pack)
        for purchased_offer in purchased_offers:
            purchased_offer_temp = copy.deepcopy(purchased_offer)
            offer_products =  list(model_to_dict(offer_product) for offer_product in purchased_offer_temp.offer_products) 
            for offer_product in offer_products:
                if offer_product["quantity"] > 0:
                    for key , product_in_pack in products_in_pack.items():
                        if key in products_in_pack_temp:
                            if product_in_pack["product"].product.id == offer_product["product"] and product_in_pack["offer"].id == offer_product["id"]:
                                if offer_product["has_options"]:
                                    product = products_in_pack_temp[offer_product["product"]]
                                    product = product["product"]
                                    variant_options = set(option for option in product.options.all())
                                    if check_options(variant_options , offer_product["options"]) :
                                        offer_product["quantity"] -= product_in_pack['quantity']
                                        products_in_pack_temp.pop(key)
                                else:
                                    offer_product["quantity"] -= product_in_pack['quantity']
                                    products_in_pack_temp.pop(key)
            if products_in_pack_temp is not None:
                pass
        #             if offer_product.has_options:
        #                 product = products_in_pack_temp[offer_product.product.id]
        #                 product = product["product"]
        #                 op_options = set(option for option in offer_product.options.all() )
        #                 variant_options = set(option for option in product.options.all())
        #                 if check_options(variant_options , op_options) and quantity != op.quantity:
        #                     products_in_pack_temp.pop(offer_product.product.id)
        #             else:
        for purchased_product in purchased_products:
            # purchased_product["purchase"] = purchase
            product = purchased_product["product"]
            quantity = purchased_product["quantity"]
            branch = validated_data['branch']       
            in_pack  = purchased_product.get("in_pack" , False)
            offer  = purchased_product.get("offer" , None)
            branch_product = Branch_Products.objects.filter(product=product , branch=branch)
            if len(branch_product) > 0:
                if branch_product[0].quantity < quantity: 
                    purchased_products_errors.append({"quantity" : "This branch don't have the needed quantity"})
                else:
                    purchased_products_errors.append({})
            else:
                purchased_products_errors.append({"product" : "This branch don't have this product"})
            purchased_product["wholesale_price"] = purchased_product["product"].wholesale_price
            purchased_product["selling_price"] = purchased_product["product"].selling_price
            purchased_product["product"] = purchased_product["product"].id
            if in_pack == True:
                purchased_product["offer"] = purchased_product["offer"].id
            # purchased_product_serialized_data = PurchasedProductsSerializer(data = purchased_product)
            # purchased_product_serialized_data.is_valid(raise_exception=True)
        if all(not d for d in purchased_products) :
            errors["purchased_products"] = purchased_products_errors
        if len(errors) > 0:
            raise serializers.ValidationError(errors)
        return validated_data
    
    def create(self, validated_data):
        purchased_products = validated_data.pop("purchased_products" , None)
        purchased_offers = validated_data.pop("purchased_offers" , None)
        if purchased_offers is not None:
            if len(purchased_offers) > 0 :
                validated_data['has_offers'] = True
        validated_data['subtotal_price'] = 0
        validated_data['total_price'] = 0
        # subtotal_price = 0
        # total_price = 0
        purchase = super().create(validated_data)
        for purchased_product in purchased_products:
            purchased_product["purchase"] = purchase.id
            # purchased_product["wholesale_price"] = purchased_product["product"].wholesale_price
            # purchased_product["selling_price"] = purchased_product["product"].selling_price
            # purchased_product["product"] = purchased_product["product"].id
            product = purchased_product.get("product" , None)
            quantity = purchased_product.get("quantity" , None)
            product = purchased_product.get("product" , None)
            quantity = purchased_product.get("quantity" , None)
            branch = purchase.branch          
            branch_product = Branch_Products.objects.filter(product=product , branch=branch).first()
            discount = calculate_discount_instance(self , product)
            if discount["discount"] is not None:
                purchased_product['discount'] = discount["discount"].id
                purchased_product['total_price'] = discount["total"] * quantity
                purchased_product['has_discount'] = True
            else:
                purchased_product['total_price'] =  discount["total"] * quantity
                purchased_product['has_discount'] = False
            branch_product.quantity -= quantity
            branch_product.save()
            purchased_product_serialized_data = PurchasedProductsSerializer(data = purchased_product)
            purchased_product_serialized_data.is_valid(raise_exception=True)
            insatnce = purchased_product_serialized_data.save()
            purchase.subtotal_price += insatnce.selling_price * insatnce.quantity
            purchase.total_price += insatnce.total_price
        for purchased_offer in purchased_offers:
            purchase.purchased_offers.add(purchased_offer)
        return purchase
    def to_representation(self, instance):
        self.fields['purchased_offers'] = OfferSerializer(many=True, read_only=True)   
        data = super(PurchaseSerializer, self).to_representation(instance)
        return data
    
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id" , "national_number" , "first_name" , "last_name" , "phone_number" , "gender" ]

    def validate(self, attrs):
        errors = {}
        validated_data = super().validate(attrs)
        national_number = validated_data.get('national_number' ,None)
        phone_number = validated_data.get('phone_number' ,None)
        if not national_number.isdigit():
            errors["national_number"] = "National number should be a number"
        if not phone_number.isdigit():
            errors["phone_number"] = "Phone number should be a number"
        
        if errors:
            raise serializers.ValidationError(errors)
        return validated_data