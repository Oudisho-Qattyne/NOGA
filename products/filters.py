import django_filters
from .models import Variant

class VariantFilter(django_filters.FilterSet):
    option = django_filters.CharFilter(field_name='options__option', lookup_expr='exact')
    attribute = django_filters.CharFilter(field_name='options__attribute__attribute', lookup_expr='exact')

    class Meta:
        model = Variant
        fields = {
            'id': ['exact'],
            'product__product_name': ['exact'],
            'quantity': ['exact'],
            'selling_price': ['exact'],
            'wholesale_price': ['exact'],
            # 'option': ['exact'],          # اسم الحقل المستخدم في URL ل options__option
            # 'attribute': ['exact'],       # اسم الحقل المستخدم في URL ل options__attribute__attribute
            # 'options__unit__unit': ['exact'],
        }
