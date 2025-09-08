from products.models import Product
from mobile.serializers import ProductSimpleSerializer
from rest_framework.response import Response

from django.utils import timezone
from datetime import datetime

def is_coupon_valid(coupon, purchase):
    """
    تحقق صلاحية الكوبون مع دعم حقول قد تكون None
    :param coupon: instance of Coupon model
    :param purchase: instance of Purchase model
    :return: True إذا صالح، False إذا غير صالح
    """
    today = timezone.now().date()

    # تحقق من تواريخ الصلاحية (إذا لم يتم تحديدها اعتبرها صالحة)
    if coupon.start_date and today < coupon.start_date:
        return False
    if coupon.end_date and today > coupon.end_date:
        return False

    # تحقق من الحدود السعرية (إذا لم يتم تحديدها اعتبرها غير محدودة)
    min_price = coupon.min_price if coupon.min_price is not None else 0
    max_price = coupon.max_price if coupon.max_price is not None else float('inf')

    if not (min_price <= purchase.subtotal_price <= max_price):
        return False

    return True


def validate_date_format(date_str):
    try:
        # Validate the date format as "yyyy-mm-dd"
        datetime.strptime(date_str, '%Y-%m-%d')
        return True  # Return True if the format is correct
    except ValueError:
        return False  # Return False if the format is incorrect

