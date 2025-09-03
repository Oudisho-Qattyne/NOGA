from products.models import Product
from mobile.serializers import ProductSimpleSerializer
from rest_framework.response import Response

from django.utils import timezone
from datetime import datetime

def is_coupon_valid(coupon):
    """
    تحقق ما إذا كان الكوبون صالحًا (تاريخ اليوم داخل فترة الصلاحية)
    :param coupon: instance of Coupon model
    :return: True if valid, False otherwise
    """
    today = timezone.now().date()
    return coupon.start_date <= today <= coupon.end_date

def validate_date_format(date_str):
    try:
        # Validate the date format as "yyyy-mm-dd"
        datetime.strptime(date_str, '%Y-%m-%d')
        return True  # Return True if the format is correct
    except ValueError:
        return False  # Return False if the format is incorrect

