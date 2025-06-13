import django_filters
from .models import Variant

class VariantFilter(django_filters.FilterSet):
    option = django_filters.CharFilter(field_name='options__option', lookup_expr='icontains')
    attribute = django_filters.CharFilter(field_name='options__attribute__attribute', lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='product__category__category', lookup_expr='icontains')
    product = django_filters.CharFilter(field_name='product__product_name', lookup_expr='icontains')
    class Meta:
        model = Variant
        fields = {
            'id': ['icontains'],
            'product__product_name': ['icontains'],
            'quantity': ['icontains'],
            'selling_price': ['icontains'],
            'wholesale_price': ['icontains'],
            'sku':['icontains']
            # 'option': ['icontains'],          # اسم الحقل المستخدم في URL ل options__option
            # 'attribute': ['icontains'],       # اسم الحقل المستخدم في URL ل options__attribute__attribute
            # 'options__unit__unit': ['icontains'],
        }
