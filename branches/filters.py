import django_filters
from .models import Branch_Products


class BranchProductFilter(django_filters.FilterSet):
    option = django_filters.CharFilter(field_name='product__options__option', lookup_expr='icontains')
    attribute = django_filters.CharFilter(field_name='product__options__attribute__attribute', lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='product__product__category__category', lookup_expr='icontains')
    product = django_filters.CharFilter(field_name='product__product__product_name', lookup_expr='icontains')
    selling_price =  django_filters.RangeFilter(field_name='product__selling_price')
    wholesale_price = django_filters.RangeFilter(field_name='product__wholesale_price')
    quantity = django_filters.RangeFilter(field_name='product__quantity')
    sku:django_filters.CharFilter(field_name='product__sku', lookup_expr='icontains')
    class Meta:
        model = Branch_Products
        fields = {
            "branch":['exact'],
            "quantity":['exact']
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