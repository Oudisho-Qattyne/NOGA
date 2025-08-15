from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
import qrcode
from PIL import Image , ImageDraw
import uuid
from products.models import Option_Unit
from django.utils import timezone
from sales.models import Discount , Discount_Category , Discount_Product
from products.models import Variant

class Paginator(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 40

def upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 2MB in bytes

# Validate the size of uploaded images
def validate_image_size(value):
    if value.size > MAX_IMAGE_SIZE:
        raise serializers.ValidationError("Image file size is too large (max 2MB)")


def genereate(image_url , product):
    A4 = Image.open(f'mediafiles/productqr/A4.jpg')
    img = Image.open(image_url)
    new_image = Image.new('RGB',(A4.width,A4.height), (250,250,250))
    number_of_rows = A4.height//img.height
    number_of_cols = A4.width//img.width

    for j in range(0 , number_of_rows): 
        for i in range(0,number_of_cols):
            draw = ImageDraw.Draw(img)
            new_image.paste(img , (img.width*i,img.height*j))
    draw = ImageDraw.Draw(new_image)
    draw.text((10, A4.height-20), "NOGA project 2025" , fill='Black' )
    draw.text((300, A4.height-20), product , fill='Black' )
    return new_image
 

def generateQR(request , id , file_nameP , folder_name):
    file_namep = file_nameP.replace(" ", "-")
    file_name = f"{file_nameP}-{id}.png"
    download_file_name = f"{file_nameP}-{id}-download.jpg"
    path = f'mediafiles/productqr'
    file_path = f"{path}/{file_name}"
    download_file_path = f"{path}/{download_file_name}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=5, border=3)
    qr.add_data(f"product-{id}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.save(file_path, 'PNG')
    download_image = genereate(file_path , f"{file_name}")
    download_image.save(download_file_path)
    qr_code = f"{request.build_absolute_uri('/')}media/productqr/{file_name}"
    qr_codes_download = f"{request.build_absolute_uri('/')}media/productqr/{download_file_name}"
    return qr_code , qr_codes_download


def generate_unique_code():
    return str(uuid.uuid4())[:8]  # Adjust the length as needed

def find_element_by_id(data_list, id):
    for element in data_list:
        if element.product.id == id:
            return element
    return None  # Return None if element with the ID is not found

def find_element_by_id2(data_list, id):
    for element in data_list:
        if element['product'] == id:
            return element
    return None  # Return None if element with the ID is not found

def generate_sku(product_name ,options):
    option_unit_list = [product_name]
    for option, unit in options.values_list('option', 'option_unit'):
        print(unit)
        if unit:
            option_unit= Option_Unit.objects.get(id=unit).unit.unit
            option_unit_list.append(f"{option}{option_unit}")
        else:
            option_unit_list.append(option)
    sku = "-".join(option_unit_list)
    return sku

def check_options(variant_options , dp_options):
    v_options = []
    p_options = []
    for option in variant_options:
        temp = option.attribute.attribute + option.option
        if option.attribute.has_unit:
            temp += Option_Unit.objects.get(option=option).unit.unit
        v_options.append(temp)
    for option in dp_options:
        temp = option.attribute.attribute + option.option
        if option.attribute.has_unit:
            temp += Option_Unit.objects.get(option=option).unit.unit
        p_options.append(temp)
    v_options = set(v_options)
    p_options = set(p_options)
    return p_options.issubset(v_options)



def is_valid_offer(offer):
    today = timezone.now().date()
    return offer.start_date <= today <= offer.end_date

def calculate_discount(self , variant):
        from sales.serializers import DiscountSimpleSerializer

        product = variant.product
        options = variant.options.all()  # Assuming variant.options is a queryset or list

        today = timezone.now().date()

        def is_valid_discount(discount):
            return discount.start_date <= today <= discount.end_date
        
        
        
        def calculate_totla_price(discount , price):
            amount = discount.amount
            type = discount.discount_type
            if type == "fixed":
                return price - amount
            elif type == "percentage":
                return price - (price * amount / 100)
            
        discounts = Discount_Product.objects.filter(
            product=product,
            discount__for_every_product_exept=False,
            discount__start_date__lte=today,
            discount__end_date__gte=today
        ).distinct()

      
        for dp in discounts:
            # If has_options is True, check if all variant options are covered
            if dp.has_options:
                dp_options = set(option for option in dp.options.all())
                variant_options = set(option for option in options)
                if check_options(variant_options,dp_options):
                    if is_valid_discount(dp.discount):
                        discount_data = DiscountSimpleSerializer(dp.discount)
                        return {
                            "discount" : discount_data.data,
                            "total" : calculate_totla_price(dp.discount , variant.selling_price)
                            }
            else:
                # Discount applies to product regardless of options
                if is_valid_discount(dp.discount):
                    discount_data = DiscountSimpleSerializer(dp.discount)
                    return {
                            "discount" : discount_data.data,
                            "total" : calculate_totla_price(dp.discount , variant.selling_price)
                            }

        # 2. Check discount for product only (without options)
        discounts_product_only = Discount.objects.filter(
            has_products=True,
            # has_categories=False,
            for_every_product_exept=False,
            discount_product__product=product,
            start_date__lte=today,
            end_date__gte=today
        ).distinct()
        if discounts_product_only.exists():
            discount_data = DiscountSimpleSerializer(discounts_product_only.first())
            return {
                    "discount" : discount_data.data,
                    "total" : calculate_totla_price(discounts_product_only.first() , variant.selling_price)
                    }

        # 3. Check discount for category and option
        category = product.category 
        discount_categories = Discount_Category.objects.filter(
            category=category,
            discount__for_every_product_exept=False,
            discount__start_date__lte=today,
            discount__end_date__gte=today
        ).distinct()

        for dc in discount_categories:
            if dc.has_options:
                dc_options = set(dc.options.all())
                variant_options = set(options)
                if check_options(variant_options,dc_options):
                    if is_valid_discount(dc.discount):
                        discount_data = DiscountSimpleSerializer(dc.discount)
                        return {
                            "discount" : discount_data.data,
                            "total" : calculate_totla_price(dc.discount , variant.selling_price)
                            }
            else:
                if is_valid_discount(dc.discount):
                    discount_data = DiscountSimpleSerializer(dc.discount)
                    return {
                            "discount" : discount_data.data,
                            "total" : calculate_totla_price(dc.discount , variant.selling_price)
                            }

        # 4. Check discount for category only
        discounts_category_only = Discount.objects.filter(
            # has_products=False,
            has_categories=True,
            for_every_product_exept=False,
            discount_category__category=category,
            start_date__lte=today,
            end_date__gte=today
        ).distinct()
        if discounts_category_only.exists():
            discount_data = DiscountSimpleSerializer(discounts_category_only.first())
            return {
                    "discount" : discount_data.data,
                    "total" : calculate_totla_price(discounts_category_only.first() , variant.selling_price)
                    }
        # ****************************************************************************************************************************************

        discounts = Discount_Product.objects.filter(
            product=product,
            discount__for_every_product_exept=True,
            discount__start_date__lte=today,
            discount__end_date__gte=today
        ).distinct()

      
        for dp in discounts:
            # If has_options is True, check if all variant options are covered
            if dp.has_options:
                dp_options = set(option for option in dp.options.all())
                variant_options = set(option for option in options)
                if not check_options(variant_options,dp_options):
                    print(check_options(variant_options,dp_options))
                    if is_valid_discount(dp.discount):
                        discount_data = DiscountSimpleSerializer(dp.discount)
                        return {
                            "discount" : discount_data.data,
                            "total" : calculate_totla_price(dp.discount , variant.selling_price)
                            }
            # else:
            #     # Discount applies to product regardless of options
            #     if is_valid_discount(dp.discount):
            #         # discount_data = DiscountSimpleSerializer(dp.discount)
            #         return {
            #                 "discount" : None,
            #                 "total" : variant.selling_price
            #                 }

        # 2. Check discount for product only (without options)
        discounts_product_only = Discount.objects.filter(
            has_products=True,
            # has_categories=False,
            for_every_product_exept=True,
            start_date__lte=today,
            end_date__gte=today
        ).exclude(
            discount_product__product=product
        ).distinct()
        if discounts_product_only.exists():
            discount_data = DiscountSimpleSerializer(discounts_product_only.first())
            return {
                    "discount" : discount_data.data,
                    "total" : calculate_totla_price(discounts_product_only.first() , variant.selling_price)
                    }

        # 3. Check discount for category and option
        category = product.category 
        discount_categories = Discount_Category.objects.filter(
            category=category,
            discount__for_every_product_exept=True,
            discount__start_date__lte=today,
            discount__end_date__gte=today
        ).distinct()

        for dc in discount_categories:
            if dc.has_options:
                dc_options = set(dc.options.all())
                variant_options = set(options)
                if not check_options(variant_options,dc_options):
                    if is_valid_discount(dc.discount):
                        discount_data = DiscountSimpleSerializer(dc.discount)
                        return {
                            "discount" : discount_data.data,
                            "total" : calculate_totla_price(dc.discount , variant.selling_price)
                            }

        # 4. Check discount for category only
        discounts_category_only = Discount.objects.filter(
            # has_products=False,
            has_categories=True,
            for_every_product_exept=True,
            start_date__lte=today,
            end_date__gte=today
        ).exclude(
            discount_category__category=category,
        ).distinct()
        if discounts_category_only.exists():
            discount_data = DiscountSimpleSerializer(discounts_category_only.first())
            return {
                    "discount" : discount_data.data,
                    "total" : calculate_totla_price(discounts_category_only.first() , variant.selling_price)
                    }


# ****************************************************************************************************************************************

        discounts_for_all_products = Discount.objects.filter(
            # has_products=True,
            # has_categories=False,
            for_every_product=True,
            for_every_product_exept=False,
            discount_product__product=product,
            start_date__lte=today,
            end_date__gte=today
        ).distinct()
        if discounts_for_all_products.exists():
            discount_data = DiscountSimpleSerializer(discounts_for_all_products.first())
            return {
                    "discount" : discount_data.data,
                    "total" : calculate_totla_price(discounts_for_all_products.first() , variant.selling_price)
                    }

        return {
                "discount" : None,
                "total" : variant.selling_price
                }  # No applicable discount found


def calculate_discount_instance(self , variant):
        from sales.serializers import DiscountSimpleSerializer
        variant = Variant.objects.get(id=variant)
        product = variant.product
        options = variant.options.all()  # Assuming variant.options is a queryset or list

        today = timezone.now().date()

        def is_valid_discount(discount):
            return discount.start_date <= today <= discount.end_date
        
        def check_options(variant_options , dp_options):
            v_options = []
            p_options = []
            for option in variant_options:
                temp = option.attribute.attribute + option.option
                if option.attribute.has_unit:
                    temp += Option_Unit.objects.get(option=option).unit.unit
                v_options.append(temp)
            for option in dp_options:
                temp = option.attribute.attribute + option.option
                if option.attribute.has_unit:
                    temp += Option_Unit.objects.get(option=option).unit.unit
                p_options.append(temp)
            v_options = set(v_options)
            p_options = set(p_options)
            print(v_options)
            print(p_options)
            return p_options.issubset(v_options)
        
        def calculate_totla_price(discount , price):
            amount = discount.amount
            type = discount.discount_type
            if type == "fixed":
                return price - amount
            elif type == "percentage":
                return price - (price * amount / 100)
            
        discounts = Discount_Product.objects.filter(
            product=product,
            discount__for_every_product_exept=False,
            discount__start_date__lte=today,
            discount__end_date__gte=today
        ).distinct()

      
        for dp in discounts:
            # If has_options is True, check if all variant options are covered
            if dp.has_options:
                dp_options = set(option for option in dp.options.all())
                variant_options = set(option for option in options)
                if check_options(variant_options,dp_options):
                    print(check_options(variant_options,dp_options))
                    if is_valid_discount(dp.discount):
                        # discount_data = DiscountSimpleSerializer(dp.discount)
                        return {
                            "discount" : dp.discount,
                            "total" : calculate_totla_price(dp.discount , variant.selling_price)
                            }
            else:
                # Discount applies to product regardless of options
                if is_valid_discount(dp.discount):
                    # discount_data = DiscountSimpleSerializer(dp.discount)
                    return {
                            "discount" :dp.discount,
                            "total" : calculate_totla_price(dp.discount , variant.selling_price)
                            }

        # 2. Check discount for product only (without options)
        discounts_product_only = Discount.objects.filter(
            has_products=True,
            # has_categories=False,
            for_every_product_exept=False,
            discount_product__product=product,
            start_date__lte=today,
            end_date__gte=today
        ).distinct()
        if discounts_product_only.exists():
            # discount_data = DiscountSimpleSerializer(discounts_product_only.first())
            return {
                    "discount" : discounts_product_only.first(),
                    "total" : calculate_totla_price(discounts_product_only.first() , variant.selling_price)
                    }

        # 3. Check discount for category and option
        category = product.category 
        discount_categories = Discount_Category.objects.filter(
            category=category,
            discount__for_every_product_exept=False,
            discount__start_date__lte=today,
            discount__end_date__gte=today
        ).distinct()

        for dc in discount_categories:
            if dc.has_options:
                dc_options = set(dc.options.all())
                variant_options = set(options)
                if check_options(variant_options,dc_options):
                    if is_valid_discount(dc.discount):
                        # discount_data = DiscountSimpleSerializer(dc.discount)
                        return {
                            "discount" : dp.discount,
                            "total" : calculate_totla_price(dc.discount , variant.selling_price)
                            }
            else:
                if is_valid_discount(dc.discount):
                    # discount_data = DiscountSimpleSerializer(dc.discount)
                    return {
                            "discount" : dp.discount,
                            "total" : calculate_totla_price(dc.discount , variant.selling_price)
                            }

        # 4. Check discount for category only
        discounts_category_only = Discount.objects.filter(
            # has_products=False,
            has_categories=True,
            for_every_product_exept=False,
            discount_category__category=category,
            start_date__lte=today,
            end_date__gte=today
        ).distinct()
        if discounts_category_only.exists():
            # discount_data = DiscountSimpleSerializer(discounts_category_only.first())
            return {
                    "discount" : discounts_category_only.first(),
                    "total" : calculate_totla_price(discounts_category_only.first() , variant.selling_price)
                    }
        # ****************************************************************************************************************************************

        discounts = Discount_Product.objects.filter(
            product=product,
            discount__for_every_product_exept=True,
            discount__start_date__lte=today,
            discount__end_date__gte=today
        ).distinct()

      
        for dp in discounts:
            # If has_options is True, check if all variant options are covered
            if dp.has_options:
                dp_options = set(option for option in dp.options.all())
                variant_options = set(option for option in options)
                if not check_options(variant_options,dp_options):
                    print(check_options(variant_options,dp_options))
                    if is_valid_discount(dp.discount):
                        # discount_data = DiscountSimpleSerializer(dp.discount)
                        return {
                            "discount" : dp.discount,
                            "total" : calculate_totla_price(dp.discount , variant.selling_price)
                            }
            # else:
            #     # Discount applies to product regardless of options
            #     if is_valid_discount(dp.discount):
            #         # discount_data = DiscountSimpleSerializer(dp.discount)
            #         return {
            #                 "discount" : None,
            #                 "total" : variant.selling_price
            #                 }

        # 2. Check discount for product only (without options)
        discounts_product_only = Discount.objects.filter(
            has_products=True,
            # has_categories=False,
            for_every_product_exept=True,
            start_date__lte=today,
            end_date__gte=today
        ).exclude(
            discount_product__product=product
        ).distinct()
        if discounts_product_only.exists():
            # discount_data = DiscountSimpleSerializer(discounts_product_only.first())
            return {
                    "discount" : discounts_product_only.first(),
                    "total" : calculate_totla_price(discounts_product_only.first() , variant.selling_price)
                    }

        # 3. Check discount for category and option
        category = product.category 
        discount_categories = Discount_Category.objects.filter(
            category=category,
            discount__for_every_product_exept=True,
            discount__start_date__lte=today,
            discount__end_date__gte=today
        ).distinct()

        for dc in discount_categories:
            if dc.has_options:
                dc_options = set(dc.options.all())
                variant_options = set(options)
                if not check_options(variant_options,dc_options):
                    if is_valid_discount(dc.discount):
                        # discount_data = DiscountSimpleSerializer(dc.discount)
                        return {
                            "discount" : dc.discoun,
                            "total" : calculate_totla_price(dc.discount , variant.selling_price)
                            }

        # 4. Check discount for category only
        discounts_category_only = Discount.objects.filter(
            # has_products=False,
            has_categories=True,
            for_every_product_exept=True,
            start_date__lte=today,
            end_date__gte=today
        ).exclude(
            discount_category__category=category,
        ).distinct()
        if discounts_category_only.exists():
            # discount_data = DiscountSimpleSerializer(discounts_category_only.first())
            return {
                    "discount" : discounts_category_only.first(),
                    "total" : calculate_totla_price(discounts_category_only.first() , variant.selling_price)
                    }


# ****************************************************************************************************************************************

        discounts_for_all_products = Discount.objects.filter(
            # has_products=True,
            # has_categories=False,
            for_every_product=True,
            for_every_product_exept=False,
            discount_product__product=product,
            start_date__lte=today,
            end_date__gte=today
        ).distinct()
        if discounts_for_all_products.exists():
            # discount_data = DiscountSimpleSerializer(discounts_for_all_products.first())
            return {
                    "discount" : discounts_for_all_products.first(),
                    "total" : calculate_totla_price(discounts_for_all_products.first() , variant.selling_price)
                    }

        return {
                "discount" : None,
                "total" : variant.selling_price
                }  # No applicable discount found
