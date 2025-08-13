import django_filters
from products.models import Product


class MobileProductFilter(django_filters.FilterSet):
    option = django_filters.CharFilter(field_name='variant__options__option', lookup_expr='icontains')
    attribute = django_filters.CharFilter(field_name='variant__options__attribute__attribute', lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='category__category', lookup_expr='icontains')
    product = django_filters.CharFilter(field_name='product_name', lookup_expr='icontains')
    price =  django_filters.RangeFilter(field_name='variant__selling_price')
    quantity = django_filters.RangeFilter(field_name='variant__quantity')
    sku:django_filters.CharFilter(field_name='variant__sku', lookup_expr='icontains')
    class Meta:
        model = Product
        fields = {
            # "quantity":['exact']
        #     'id': ['icontains'],
        #     'product__product_name': ['icontains'],
        #     'quantity': ['icontains'],
        #     'selling_price': ['icontains'],
        #     'wholesale_price': ['icontains'],
        #     'sku':['icontains']
        #     # 'option': ['icontains'],          # اسم الحقل المستخدم في URL ل options__option
        #     # 'attribute': ['icontains'],       # اسم الحقل المستخدم في URL ل options__attribute__attribute
        #     # 'options__unit__unit': ['icontains'],
        }