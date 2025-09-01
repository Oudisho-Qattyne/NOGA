from ..models import AssociationRule
from products.models import Product
from mobile.serializers import ProductSimpleSerializer
from rest_framework.response import Response
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
            product=Product.objects.filter(id__in=unique_id)
            serializer=ProductSimpleSerializer(product)
    return Response(serializer.data)
