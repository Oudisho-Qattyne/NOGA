from ..models import AssociationRule
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


def get_sales_stats():
    """إرجاع إحصائيات المبيعات (عدد المعاملات مثلاً)."""
    return {
        "total_rules": AssociationRule.objects.count(),
        "max_lift": AssociationRule.objects.order_by("-lift").first().lift if AssociationRule.objects.exists() else 0,
    }

def get_analysis_stats():
    """إرجاع إحصائيات خاصة بتحليل القواعد."""
    return {
        "high_confidence_rules": AssociationRule.objects.filter(confidence__gte=0.7).count(),
        "medium_rules": AssociationRule.objects.filter(confidencegte=0.4, confidencelt=0.7).count(),
    }


def get_product_recommendations(product_id):
    """إرجاع منتجات موصى بها بناءً على القواعد."""
    rules = AssociationRule.objects.filter(antecedents__icontains=product_id).order_by("-confidence")
    recs = []
    unique_id=set()
    for r in rules[:10]:
        for pid in r.consequents:
            unique_id.add(pid)
    # product=Product.objects.filter(id__in=unique_id)
    # serializer=ProductSimpleSerializer(product)
    # return Response(serializer.data)
    return unique_id