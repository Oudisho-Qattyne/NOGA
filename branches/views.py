from django.shortcuts import render
from .models import *
from rest_framework import generics
from .serializers import *
from rest_framework import filters
from django_filters import rest_framework as filter
from NOGA.utils import *
from .filters import *
from products.models import Attribute
from django.http import StreamingHttpResponse
import time
from django.http import JsonResponse, HttpResponseBadRequest, Http404
from .models import Branch, Branch_Products
from rest_framework.decorators import api_view
from .utils import *
# Create your views here.

class BranchsAPIView(generics.ListAPIView , generics.ListCreateAPIView ):
    queryset= Branch.objects.all()
    serializer_class = BranchSerializer
    pagination_class = Paginator
    filter_backends = [filter.DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
    filterset_fields = ["id" , "number" ,"city" , "area" , "street" , "manager"]
    search_fields = ["id" , "number" , "location"  , "area" , "street" ]
    ordering_fields = ["id" , "number" ,"city" , "area" , "street" , "manager"]
    
    
class BranchAPIView( generics.RetrieveAPIView, generics.DestroyAPIView , generics.UpdateAPIView ):
    queryset= Branch.objects.all()
    serializer_class = BranchSerializer


class CitiesAPIView(generics.ListAPIView , generics.ListCreateAPIView ):
    queryset= City.objects.all()
    serializer_class = CitySerializer
    filter_backends = [filter.DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
    pagination_class = Paginator
    filterset_fields = ["id" ,"city_name"]
    search_fields = ["id" , "city_name"]
    ordering_fields = ["id" ,"city_name"]
  
class CityAPIView( generics.RetrieveAPIView, generics.DestroyAPIView , generics.UpdateAPIView ):
    queryset= City.objects.all()
    serializer_class = CitySerializer

class BranchProductsAPIView(generics.ListAPIView):
    queryset = Branch_Products.objects.all()
    serializer_class = BranchProductsSerializer
    filter_backends=[filter.DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
    filterset_class = BranchProductFilter  
    pagination_class = Paginator
    search_fields = [
        "id",
        "product__product__product__product_name",
        "product__product__quantity",
        "product__product__selling_price",
        "product__product__wholesale_price",
        "product__product__options__option",
        # "options__unit__unit",
        "product__product__options__attribute__attribute", 
        "product__product__sku"
    ]
    ordering_fields = [
        "product__id",
        "product__product__product_name",
        "product__quantity",
        "product__selling_price",
        "product__wholesale_price",
        "product__options__option",
        # "options__unit__unit",
        "product__options__attribute__attribute",
        "product__sku"
    ]
    def get_queryset(self):
        queryset = super().get_queryset()
        attribute_names = Attribute.objects.values_list('attribute', flat=True)

        # Convert the QuerySet to a list
        attribute_names_list = list(attribute_names)
        for key, value in self.request.query_params.items():
            if key in attribute_names_list: 
                value = value.split(',')
                queryset = queryset.filter(
                product__options__attribute__attribute=key,
                product__options__option__in=value
            )
        return queryset.distinct()

class CamerasApiView(generics.CreateAPIView , generics.ListAPIView):
    queryset = Camera.objects.all()
    serializer_class = CamerasSerializer
    filter_backends=[filter.DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
    pagination_class = Paginator
    search_fields = [
        "id",
        "camera_type",
        "source_url",
        "view_url",
        "branch__city__city_name",
        "is_active",
        "branch"

    ]
    ordering_fields = [
        "id",
        "source_url",
        "view_url",
        "view_source",
        "branch__city__city_name",
        "is_active",
        "branch"

    ]
    filterset_fields = [
        "id",
        "camera_type",
        "source_url",
        "view_url",
        "branch__city__city_name",
        "is_active",
        "branch"
    ]

class CameraApiView(generics.DestroyAPIView , generics.UpdateAPIView):
    queryset = Camera.objects.all()
    serializer_class = CamerasSerializer



@api_view(['GET'])
def find_nearest_branch_with_product(request):
    # جلب المعطيات من GET أو POST (مثلاً GET هنا)
    product_id = request.GET.get('product')
    wanted_quantity = request.GET.get('quantity')
    current_branch_id = request.GET.get('current_branch')

    # التحقق من صحة المعطيات
    if not product_id or not wanted_quantity or not current_branch_id:
        return HttpResponseBadRequest("Missing parameters")

    try:
        wanted_quantity = int(wanted_quantity)
        current_branch = Branch.objects.get(id=current_branch_id)
    except ValueError:
        return HttpResponseBadRequest("Invalid quantity")
    except Branch.DoesNotExist:
        return Http404("Current branch not found")

    # جلب موقع الفرع الحالي وتحليله
    try:
        current_location = parse_location(current_branch.location)
        print(current_location)
    except Exception:
        return HttpResponseBadRequest("Invalid location format in current branch")

    # جلب جميع الفروع التي تمتلك المنتج والكمية المطلوبة أو أكثر
    branch_products = Branch_Products.objects.filter(
        product_id=product_id,
        quantity__gte=wanted_quantity
    ).exclude(id=current_branch_id).select_related('branch')

    if not branch_products.exists():
        return JsonResponse({"message": "No branch has the requested product quantity"}, status=404)

    # إيجاد أقرب فرع بناءً على المسافة
    min_distance = float('inf')
    nearest_branch = None

    for bp in branch_products:
        try:
            branch_location = parse_location(bp.branch.location)
        except Exception:
            continue  # تجاهل الفروع ذات الإحداثيات غير الصحيحة

        dist = haversine(current_location, branch_location)
        if dist < min_distance:
            min_distance = dist
            nearest_branch = bp.branch

    if not nearest_branch:
        return JsonResponse({"message": "No valid branch location found"}, status=404)

    # إعادة النتيجة
    return JsonResponse({
        "nearest_branch": {
            "id": nearest_branch.id,
            "city": nearest_branch.city.city_name,
            "number": nearest_branch.number,
            "area": nearest_branch.area,
            "street": nearest_branch.street,
            "location": nearest_branch.location,
            "distance_km": round(min_distance, 2)
        }
    })