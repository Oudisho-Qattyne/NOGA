from django.utils import timezone

def is_coupon_valid(coupon):
    """
    تحقق ما إذا كان الكوبون صالحًا (تاريخ اليوم داخل فترة الصلاحية)
    :param coupon: instance of Coupon model
    :return: True if valid, False otherwise
    """
    today = timezone.now().date()
    return coupon.start_date <= today <= coupon.end_date