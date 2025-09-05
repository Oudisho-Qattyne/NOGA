from django.shortcuts import render
from rest_framework.views import APIView , Response , status
from rest_framework import generics ,viewsets,status ,filters 
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from .models import *
from .serializers import *
from django.db.models.deletion import ProtectedError
from rest_framework.decorators import api_view , permission_classes
from django_filters.rest_framework import DjangoFilterBackend

from .utils.helpers import *




from django.db.models import Count , Sum , ExpressionWrapper , F
from django.db.models.functions import Concat

# Create your views here.

class DiscountsAPIView(generics.ListAPIView , generics.CreateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer


class DiscountAPIView(generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.has_products:
                products = Discount_Product.objects.filter(discount=instance)
                for product in products:
                    if product.has_options:
                        Discount_Product_Option.objects.filter(discount_product=product).delete()
                    product.delete()
            if instance.has_categories:
                categories = Discount_Category.objects.filter(discount = instance)
                for category in categories:
                    if category.has_options:
                        Discount_Category_Option.objects.filter(discount_category=category).delete()
                    category.delete()
            super().delete(request, *args, **kwargs)
            return Response({"message": "Discount deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Response({"message": "Discount can't be deleted"}, status=status.HTTP_400_BAD_REQUEST)
        

class DiscountsAPIView(generics.ListAPIView , generics.CreateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer


class DiscountAPIView(generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.has_products:
                products = Discount_Product.objects.filter(discount=instance)
                for product in products:
                    if product.has_options:
                        Discount_Product_Option.objects.filter(discount_product=product).delete()
                    product.delete()
            if instance.has_categories:
                categories = Discount_Category.objects.filter(discount = instance)
                for category in categories:
                    if category.has_options:
                        Discount_Category_Option.objects.filter(discount_category=category).delete()
                    category.delete()
            super().delete(request, *args, **kwargs)
            return Response({"message": "Discount deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Response({"message": "Discount can't be deleted"}, status=status.HTTP_400_BAD_REQUEST)
        

# class OffersAPIView(generics.ListAPIView , generics.CreateAPIView):
#     queryset = Offer.objects.all()
#     serializer_class = OfferSerializer


# class OfferAPIView(generics.DestroyAPIView, generics.UpdateAPIView):
#     queryset = Offer.objects.all()
#     serializer_class = OfferSerializer
#     def delete(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             products = Offer_Product.objects.filter(offer=instance)
#             for product in products:
#                 if product.has_options:
#                     Offer_Product_Option.objects.filter(offer_product=product).delete()
#                 product.delete()
            
#             super().delete(request, *args, **kwargs)
#             return Response({"message": "Offer deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
#         except ProtectedError:
#             return Response({"message": "Offer can't be deleted"}, status=status.HTTP_400_BAD_REQUEST)
        
class CouponsAPIView(generics.CreateAPIView , generics.ListAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

class CouponAPIView(generics.UpdateAPIView , generics.DestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

class PurchasesAPIView(generics.CreateAPIView , generics.ListAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

class PurchaseAPIView(generics.UpdateAPIView , generics.DestroyAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.status == "pending":
                products = Purchased_Products.objects.filter(purchase=instance)
                for product in products:
                    branch = instance.branch          
                    branch_product = Branch_Products.objects.filter(product=product.product , branch=branch).first()
                    branch_product.quantity += product.quantity
                    branch_product.save()
                    product.delete()
                super().delete(request, *args, **kwargs)
                return Response({"message": "purchase deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            return Response({"message": "purchase can't be deleted"}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Response({"message": "purchase can't be deleted"}, status=status.HTTP_400_BAD_REQUEST)

class CustomersAPIVIew(generics.CreateAPIView , generics.ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class CustomerAPIVIew(generics.UpdateAPIView , generics.DestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

@api_view(['POST'])
def ProcessPurchase(request , pk):
    try:
        purchase_instance = Purchase.objects.get(id=pk)
        if purchase_instance.status != "pending":
            return Response({"message" : "Purchase may have been processed."} , status=status.HTTP_404_NOT_FOUND)
        coupon_code = request.data.get('coupon' ,None)
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
            except Coupon.DoesNotExist:
                return Response({"message" : "Coupon not found."} , status=status.HTTP_404_NOT_FOUND)

            if is_coupon_valid(coupon , purchase_instance):
                purchase_instance.coupon = coupon
                purchase_instance.has_coupon = True
                if coupon.discount_type == 'fixed':
                    purchase_instance.total_price = purchase_instance.subtotal_price - coupon.amount
                elif coupon.discount_type == 'percentage':
                    purchase_instance.total_price = purchase_instance.subtotal_price - purchase_instance.subtotal_price * coupon.amount
        purchase_instance.status = "processing"
        purchase_instance.save()  # حفظ التغييرات

        # استدعاء السيريالايزر المناسب، هنا لنفترض أنه PurchaseSerializer
        serializer = PurchaseSerializer(purchase_instance)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except Purchase.DoesNotExist:
        return Response({"message" : "Purchase not found."} , status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
def CompletePurchase(request , pk):
    try:
        purchase_instance = Purchase.objects.get(id=pk)
        if purchase_instance.status != "processing":
            return Response({"message" : "Purchase may have been completed."} , status=status.HTTP_400_BAD_REQUEST)
        purchase_instance.status = "completed"
        purchase_instance.save()  # حفظ التغييرات

        # استدعاء السيريالايزر المناسب، هنا لنفترض أنه PurchaseSerializer
        serializer = PurchaseSerializer(purchase_instance)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except Purchase.DoesNotExist:
        return Response({"message" : "Purchase not found."} , status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
def CancelPurchase(request , pk):
    try:
        purchase_instance = Purchase.objects.get(id=pk)
        if purchase_instance.status == "completed":
            return Response({"message" : "Purchase already completed."} , status=status.HTTP_400_BAD_REQUEST)
        if purchase_instance.status == "cancelled":
            return Response({"message" : "Purchase already cancelled."} , status=status.HTTP_400_BAD_REQUEST)
        purchase_instance.status = "cancelled"
        purchase_instance.save()  # حفظ التغييرات
        products = Purchased_Products.objects.filter(purchase=purchase_instance)
        for product in products:
            branch = purchase_instance.branch          
            branch_product = Branch_Products.objects.filter(product=product.product , branch=branch).first()
            branch_product.quantity += product.quantity
            branch_product.save()

        # استدعاء السيريالايزر المناسب، هنا لنفترض أنه PurchaseSerializer
        serializer = PurchaseSerializer(purchase_instance)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except Purchase.DoesNotExist:
        return Response({"message" : "Purchase not found."} , status=status.HTTP_404_NOT_FOUND)
    
# class AssociationRuleViewSet(viewsets.ModelViewSet):
#     queryset=AssociationRule.objects.all()
#     serializer_class=AssociationRuleSerializer
#     filter_backends=[DjangoFilterBackend,filters.OrderingFilter,filters.SearchFilter]
#     filterset_fields = ['lift', 'confidence', 'support']  # تصفية حسب القيم
#     search_fields = ['antecedents', 'consequents']  
#     @action(detail=False,methods=['post'])
#     def update_rules(self,request):
#         try:
#             result=update_association_rules()
#             return Response({"message":result},status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
#     @action(detail=True, methods=['get'])
#     def recommendations(self, request,*args,**kwargs):
#         # product_id = request.query_params.get("product_id")
#         product_id=kwargs.get('pk')
#         if not product_id:
#             return Response({"error": "product_id مطلوب"}, status=400)
#         try:
#             recs = get_product_recommendations(int(product_id))
#             return Response({"recommendations": recs})

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#     @action(detail=False, methods=["get"])
#     def stats(self, request):
#         return Response({
#             "sales_stats": get_sales_stats(),
#             "analysis_stats": get_analysis_stats(),
#         })


# @api_view(['GET','post'])
# def hello(request):
#      rule=generate_association_rules_df()
#      save_association_rules(rule)
#      return Response({"message":"hello"})
    



#---------ststistics--------
@api_view(["GET"])
def TotalIncome(request):
    # branch_id = request.query_params.get('branch_id', None)
    month = request.query_params.get('month', None)
    year = request.query_params.get('year', None)
    day = request.query_params.get('day', None)
    statistics=Purchased_Products.objects.all()
    if month:
        if validate_date_format(month):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = month.split('-')[0] , purchase_id__date_of_purchase__month = month.split('-')[1])
            statistics = statistics.annotate(total=ExpressionWrapper(F('selling_price') * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_income = Sum('total'))
            if(statistics['total_income']):
                return(Response(statistics))
            else:
                return(Response({'total_income':0.0}))
        else: 
            return Response({"month" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif year:
        if validate_date_format(year):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = year.split('-')[0])
            
            statistics = statistics.annotate(total=ExpressionWrapper(F('selling_price') * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_income = Sum('total'))
            if(statistics['total_income']):
                return(Response(statistics))
            else:
                return(Response({'total_income':0.0}))
        else: 
            return Response({"year" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif day:
        if validate_date_format(day):
            statistics = statistics.filter( purchase_id__date_of_purchase__year = day.split('-')[0] , purchase_id__date_of_purchase__day = day.split('-')[2] ,  purchase_id__date_of_purchase__month = day.split('-')[1])
            
            statistics = statistics.annotate(total=ExpressionWrapper(F('selling_price') * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_income = Sum('total'))
            if(statistics['total_income']):
                return(Response(statistics))
            else:
                return(Response({'total_income':0.0}))
        else: 
            return Response({"day" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    else:
        statistics = statistics.annotate(total=ExpressionWrapper(F('selling_price') * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_income = Sum('total'))
        if(statistics['total_income']):
            return(Response(statistics))
        else:
            return(Response({'total_income':0.0}))
        
        
@api_view(["GET"])
def TotalIncomePerBranch(request , branch_id):
    month = request.query_params.get('month', None)
    year = request.query_params.get('year', None)
    day = request.query_params.get('day', None)
    
    statistics=Purchased_Products.objects.filter(purchase_id__branch_id=branch_id)
    if month:
        if validate_date_format(month):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = month.split('-')[0] ,purchase_id__date_of_purchase__month = month.split('-')[1])
            statistics = statistics.annotate(total=ExpressionWrapper(F('selling_price') * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_income = Sum('total'))
            if(statistics['total_income']):
                return(Response(statistics))
            else:
                return(Response({'total_income':0.0}))
        else: 
            return Response({"month" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif year:
        if validate_date_format(year):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = year.split('-')[0])
            statistics = statistics.annotate(total=ExpressionWrapper(F('selling_price') * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_income = Sum('total'))
            if(statistics['total_income']):
                return(Response(statistics))
            else:
                return(Response({'total_income':0.0}))
        else: 
            return Response({"year" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif day:
        if validate_date_format(day):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = day.split('-')[0] ,purchase_id__date_of_purchase__day = day.split('-')[2] , purchase_id__date_of_purchase__month = day.split('-')[1])
            
            statistics = statistics.annotate(total=ExpressionWrapper(F('selling_price') * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_income = Sum('total'))
            if(statistics['total_income']):
                return(Response(statistics))
            else:
                return(Response({'total_income':0.0}))
        else: 
            return Response({"day" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    else:
        statistics = statistics.annotate(total=ExpressionWrapper(F('selling_price') * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_income = Sum('total'))
        if(statistics['total_income']):
            return(Response(statistics))
        else:
            return(Response({'total_income':0.0}))
        

@api_view(["GET"])
def TotalIncomeAllBranch(request):
    month = request.query_params.get('month', None)
    year = request.query_params.get('year', None)
    day = request.query_params.get('day', None)
    
    statistics=Purchased_Products.objects.all()
    if month:
        if validate_date_format(month):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = month.split('-')[0] ,purchase_id__date_of_purchase__month = month.split('-')[1])
            # statistics = statistics.annotate(total=ExpressionWrapper(F('selling_price') * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_income = Sum('total'))
            statistics=statistics.values("purchase_id__branch_id"  ).annotate(branch_id = ExpressionWrapper(F("purchase_id__branch_id") , output_field=models.CharField(max_length=10)) ).values('branch_id').annotate(total=Sum(ExpressionWrapper(F('selling_price') * F('purchased_quantity'), output_field=models.DecimalField())) ).annotate(branch_name = ExpressionWrapper(Concat(F("purchase_id__branch_id__city__city_name") , F('purchase_id__branch_id__number')) , output_field=models.CharField(max_length=100)))
            
            if(statistics):
                return(Response(statistics))
            else:
                return(Response({'total_income':0.0}))
        else: 
            return Response({"month" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif year:
        if validate_date_format(year):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = year.split('-')[0])
            statistics=statistics.values("purchase_id__branch_id"  ).annotate(branch_id = ExpressionWrapper(F("purchase_id__branch_id") , output_field=models.CharField(max_length=10)) ).values('branch_id').annotate(total=Sum(ExpressionWrapper(F('selling_price') * F('purchased_quantity'), output_field=models.DecimalField())) ).annotate(branch_name = ExpressionWrapper(Concat(F("purchase_id__branch_id__city__city_name") , F('purchase_id__branch_id__number')) , output_field=models.CharField(max_length=100)))
            
            if(statistics):
                return(Response(statistics))
            else:
                return(Response({'total_income':0.0}))
        else: 
            return Response({"year" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif day:
        if validate_date_format(day):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = day.split('-')[0] ,purchase_id__date_of_purchase__day = day.split('-')[2] , purchase_id__date_of_purchase__month = day.split('-')[1])
            
            statistics=statistics.values("purchase_id__branch_id"  ).annotate(branch_id = ExpressionWrapper(F("purchase_id__branch_id") , output_field=models.CharField(max_length=10)) ).values('branch_id').annotate(total=Sum(ExpressionWrapper(F('selling_price') * F('purchased_quantity'), output_field=models.DecimalField())) ).annotate(branch_name = ExpressionWrapper(Concat(F("purchase_id__branch_id__city__city_name") , F('purchase_id__branch_id__number')) , output_field=models.CharField(max_length=100)))
            
            if(statistics):
                return(Response(statistics))
            else:
                return(Response({'total_income':0.0}))
        else: 
            return Response({"day" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    else:
        statistics=statistics.values("purchase_id__branch_id"  ).annotate(branch_id = ExpressionWrapper(F("purchase_id__branch_id") , output_field=models.CharField(max_length=10)) ).values('branch_id').annotate(total=Sum(ExpressionWrapper(F('selling_price') * F('purchased_quantity'), output_field=models.DecimalField())) ).annotate(branch_name = ExpressionWrapper(Concat(F("purchase_id__branch_id__city__city_name") , F('purchase_id__branch_id__number')) , output_field=models.CharField(max_length=100)))
        
        if(statistics):
            return(Response(statistics))
        else:
            return(Response({'total_income':0.0}))
 
@api_view(["GET"])
def TotaEarnings(request):
    # branch_id = request.query_params.get('branch_id', None)
    month = request.query_params.get('month', None)
    year = request.query_params.get('year', None)
    day = request.query_params.get('day', None)
        

    statistics=Purchased_Products.objects.all()
    if month:
        if validate_date_format(month):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = month.split('-')[0] , purchase_id__date_of_purchase__month = month.split('-')[1])
            statistics = statistics.annotate(total=ExpressionWrapper((F('selling_price') - F('wholesale_price')) * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_earning = Sum('total'))
            if(statistics['total_earning']):
                return(Response(statistics))
            else:
                return(Response({'total_earning':0.0}))
        else: 
            return Response({"month" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif year:
        if validate_date_format(year):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = year.split('-')[0])
            
            statistics = statistics.annotate(total=ExpressionWrapper((F('selling_price') - F('wholesale_price')) * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_earning = Sum('total'))
            if(statistics['total_earning']):
                return(Response(statistics))
            else:
                return(Response({'total_earning':0.0}))
        else: 
            return Response({"year" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif day:
        if validate_date_format(day):
            statistics = statistics.filter( purchase_id__date_of_purchase__year = day.split('-')[0] , purchase_id__date_of_purchase__day = day.split('-')[2] ,  purchase_id__date_of_purchase__month = day.split('-')[1])
            
            statistics = statistics.annotate(total=ExpressionWrapper((F('selling_price') - F('wholesale_price')) * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_earning = Sum('total'))
            if(statistics['total_earning']):
                return(Response(statistics))
            else:
                return(Response({'total_earning':0.0}))
        else: 
            return Response({"day" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    else:
        statistics = statistics.annotate(total=ExpressionWrapper((F('selling_price') - F('wholesale_price')) * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_earning = Sum('total'))
        if(statistics['total_earning']):
            return(Response(statistics))
        else:
            return(Response({'total_earning':0.0}))
   
  
@api_view(["GET"])
def TotalEarningPerBranch(request , branch_id):
    month = request.query_params.get('month', None)
    year = request.query_params.get('year', None)
    day = request.query_params.get('day', None)
    
    statistics=Purchased_Products.objects.filter(purchase_id__branch_id=branch_id)
    if month:
        if validate_date_format(month):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = month.split('-')[0] ,purchase_id__date_of_purchase__month = month.split('-')[1])
            statistics = statistics.annotate(total=ExpressionWrapper((F('selling_price') - F('wholesale_price')) * F('purchased_quantity'), output_field=models.DecimalField())).aggregate(total_earning = Sum('total'))
            if(statistics['total_earning']):
                return(Response(statistics))
            else:
                return(Response({'total_earning':0.0}))
        else: 
            return Response({"month" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif year:
        if validate_date_format(year):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = year.split('-')[0])
            statistics = statistics.annotate(total=ExpressionWrapper((F('selling_price') - F('wholesale_price')) * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_earning = Sum('total'))
            if(statistics['total_earning']):
                return(Response(statistics))
            else:
                return(Response({'total_earning':0.0}))
        else: 
            return Response({"year" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif day:
        if validate_date_format(day):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = day.split('-')[0] ,purchase_id__date_of_purchase__day = day.split('-')[2] , purchase_id__date_of_purchase__month = day.split('-')[1])
            
            statistics = statistics.annotate(total=ExpressionWrapper((F('selling_price') - F('wholesale_price')) * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_earning = Sum('total'))
            if(statistics['total_earning']):
                return(Response(statistics))
            else:
                return(Response({'total_earning':0.0}))
        else: 
            return Response({"day" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    else:
        statistics = statistics.annotate(total=ExpressionWrapper((F('selling_price') - F('wholesale_price')) * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_earning = Sum('total'))
        if(statistics['total_earning']):
            return(Response(statistics))
        else:
            return(Response({'total_earning':0.0}))
        
        
@api_view(["GET"])
def TotalEarningAllBranch(request):
    month = request.query_params.get('month', None)
    year = request.query_params.get('year', None)
    day = request.query_params.get('day', None)
    
    statistics=Purchased_Products.objects.all()
    if month:
        if validate_date_format(month):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = month.split('-')[0] ,purchase_id__date_of_purchase__month = month.split('-')[1])
            # statistics = statistics.annotate(total=ExpressionWrapper(F('selling_price') * F('purchased_quantity'), output_field=models.DecimalField()) ).aggregate(total_income = Sum('total'))
            statistics=statistics.values("purchase_id__branch_id"  ).annotate(branch_id = ExpressionWrapper(F("purchase_id__branch_id") , output_field=models.CharField(max_length=10)) ).values('branch_id').annotate(total_earning=Sum(ExpressionWrapper((F('selling_price') - F('wholesale_price')) * F('purchased_quantity'), output_field=models.DecimalField()) ) ).annotate(branch_name = ExpressionWrapper(Concat(F("purchase_id__branch_id__city__city_name") , F('purchase_id__branch_id__number')) , output_field=models.CharField(max_length=100)))
            
            if(statistics):
                return(Response(statistics))
            else:
                return(Response([]))
        else: 
            return Response({"month" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif year:
        if validate_date_format(year):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = year.split('-')[0])
            statistics=statistics.values("purchase_id__branch_id"  ).annotate(branch_id = ExpressionWrapper(F("purchase_id__branch_id") , output_field=models.CharField(max_length=10)) ).values('branch_id').annotate(total_earning=Sum(ExpressionWrapper((F('selling_price') - F('wholesale_price')) * F('purchased_quantity'), output_field=models.DecimalField()) ) ).annotate(branch_name = ExpressionWrapper(Concat(F("purchase_id__branch_id__city__city_name") , F('purchase_id__branch_id__number')) , output_field=models.CharField(max_length=100)))
            
            if(statistics):
                return(Response(statistics))
            else:
                return(Response([]))
        else: 
            return Response({"year" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif day:
        if validate_date_format(day):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = day.split('-')[0] ,purchase_id__date_of_purchase__day = day.split('-')[2] , purchase_id__date_of_purchase__month = day.split('-')[1])
            
            statistics=statistics.values("purchase_id__branch_id"  ).annotate(branch_id = ExpressionWrapper(F("purchase_id__branch_id") , output_field=models.CharField(max_length=10)) ).values('branch_id').annotate(total_earning=Sum(ExpressionWrapper((F('selling_price') - F('wholesale_price')) * F('purchased_quantity'), output_field=models.DecimalField()) ) ).annotate(branch_name = ExpressionWrapper(Concat(F("purchase_id__branch_id__city__city_name") , F('purchase_id__branch_id__number')) , output_field=models.CharField(max_length=100)))
            
            if(statistics):
                return(Response(statistics))
            else:
                return(Response([]))
        else: 
            return Response({"day" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    else:
        statistics=statistics.values("purchase_id__branch_id"  ).annotate(branch_id = ExpressionWrapper(F("purchase_id__branch_id") , output_field=models.CharField(max_length=10)) ).values('branch_id').annotate(total_earning=Sum(ExpressionWrapper((F('selling_price') - F('wholesale_price')) * F('purchased_quantity'), output_field=models.DecimalField()) ) ).annotate(branch_name = ExpressionWrapper(Concat(F("purchase_id__branch_id__city__city_name") , F('purchase_id__branch_id__number')) , output_field=models.CharField(max_length=100)))
            
        if(statistics):
            return(Response(statistics))
        else:
            return(Response([]))
 
@api_view(["GET"])
def TotalProducts(request):
    month = request.query_params.get('month', None)
    year = request.query_params.get('year', None)
    day = request.query_params.get('day', None)
    
    statistics=Purchased_Products.objects.all()
    if month:
        if validate_date_format(month):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = month.split('-')[0] ,purchase_id__date_of_purchase__month = month.split('-')[1])
            statistics=statistics.values("product__product").annotate(total=Sum('quantity')).annotate(product_name = ExpressionWrapper(F("product__product__product_name") , output_field=models.CharField(max_length=100))).values(
    product_id=F("product__product"),
    # total=F("total"),
    # product_name=F("product_name")
).order_by("-total")
            
            if(statistics):
                return(Response(statistics))
            else:
                return(Response([]))
        else: 
            return Response({"month" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif year:
        if validate_date_format(year):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = year.split('-')[0])
            statistics=statistics.values("product__product").annotate(total=Sum('quantity')).annotate(product_name = ExpressionWrapper(F("product__product__product_name") , output_field=models.CharField(max_length=100))).values(
    product_id=F("product__product"),
    # total=F("total"),
    # product_name=F("product_name")
).order_by("-total")
            
            if(statistics):
                return(Response(statistics))
            else:
                return(Response([]))
        else: 
            return Response({"year" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif day:
        if validate_date_format(day):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = day.split('-')[0] ,purchase_id__date_of_purchase__day = day.split('-')[2] , purchase_id__date_of_purchase__month = day.split('-')[1])
            statistics=statistics.values("product__product").annotate(total=Sum('quantity')).annotate(product_name = ExpressionWrapper(F("product__product__product_name") , output_field=models.CharField(max_length=100))).values(
    product_id=F("product__product"),
    # total=F("total"),
    # product_name=F("product_name")
).order_by("-total")
            if(statistics):
                return(Response(statistics))
            else:
                return(Response([]))
        else: 
            return Response({"day" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    else:
        statistics=statistics.values("product__product").annotate(total=Sum('quantity')).annotate(product_name = ExpressionWrapper(F("product__product__product_name") , output_field=models.CharField(max_length=100))).values(
    product_id=F("product__product"),
    # total=F("total"),
    # product_name=F("product_name")
).order_by("-total")
            
        if(statistics):
            return(Response(statistics))
        else:
            return(Response([]))
 
@api_view(["GET"])
def TotalProductsPerBranch(request , branch_id):
    month = request.query_params.get('month', None)
    year = request.query_params.get('year', None)
    day = request.query_params.get('day', None)
    
    statistics=Purchased_Products.objects.filter(purchase_id__branch_id=branch_id)

    if month:
        if validate_date_format(month):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = month.split('-')[0] ,purchase_id__date_of_purchase__month = month.split('-')[1])
            statistics=statistics.values("product_id").annotate(total=Sum('purchased_quantity')).annotate(product_name = ExpressionWrapper(F("product_id__product_name") , output_field=models.CharField(max_length=100))).order_by("-total")
            
            if(statistics):
                return(Response(statistics))
            else:
                return(Response([]))
        else: 
            return Response({"month" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif year:
        if validate_date_format(year):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = year.split('-')[0])
            statistics=statistics.values("product_id").annotate(total=Sum('purchased_quantity')).annotate(product_name = ExpressionWrapper(F("product_id__product_name") , output_field=models.CharField(max_length=100))).order_by("-total")
            
            if(statistics):
                return(Response(statistics))
            else:
                return(Response([]))
        else: 
            return Response({"year" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif day:
        if validate_date_format(day):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = day.split('-')[0] ,purchase_id__date_of_purchase__day = day.split('-')[2] , purchase_id__date_of_purchase__month = day.split('-')[1])
            statistics=statistics.values("product_id").annotate(total=Sum('purchased_quantity')).annotate(product_name = ExpressionWrapper(F("product_id__product_name") , output_field=models.CharField(max_length=100))).order_by("-total")
            if(statistics):
                return(Response(statistics))
            else:
                return(Response([]))
        else: 
            return Response({"day" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    else:
        statistics=statistics.values("product_id").annotate(total=Sum('purchased_quantity')).annotate(product_name = ExpressionWrapper(F("product_id__product_name") , output_field=models.CharField(max_length=100))).order_by("-total")
            
        if(statistics):
            return(Response(statistics))
        else:
            return(Response([]))

def calcBranchesProductsQuantities(statistics):
    res = []
    branches = {}
    for branch in statistics:
        if branch['purchase_id__branch_id'] in branches.keys():
            res[branches[branch['purchase_id__branch_id']]]['products'].append(
                {
                    "product_id":branch['product_id'],
                    "product_name":branch['product_name'],
                    "total":branch['total']
                }
            )
        else:
            branches[branch['purchase_id__branch_id']] = len(res)
            res.append({
                "branch_id":branch['purchase_id__branch_id'],
                "branch_name":branch['branch_name'],
                "products":[
                    {
                        "product_id":branch['product_id'],
                        "product_name":branch['product_name'],
                        "total":branch['total']
                    }
                ]
            })
    return res

@api_view(["GET"])
def TotalProductsAllBranch(request):
    month = request.query_params.get('month', None)
    year = request.query_params.get('year', None)
    day = request.query_params.get('day', None)
    
    statistics=Purchased_Products.objects.all()

    if month:
        if validate_date_format(month):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = month.split('-')[0] ,purchase_id__date_of_purchase__month = month.split('-')[1])
            statistics=statistics.values('purchase_id__branch_id' , "product_id").annotate(total=Sum('purchased_quantity')).annotate(branch_name = ExpressionWrapper(Concat(F("purchase_id__branch_id__city__city_name") , F('purchase_id__branch_id__number')) , output_field=models.CharField(max_length=100))).annotate(product_name = ExpressionWrapper(F("product_id__product_name") , output_field=models.CharField(max_length=100))).order_by("-total")
            res = calcBranchesProductsQuantities(statistics)
            if(statistics):
                return(Response(res))
            else:
                return(Response([]))
        else: 
            return Response({"month" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif year:
        if validate_date_format(year):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = year.split('-')[0])
            statistics=statistics.values('purchase_id__branch_id' , "product_id").annotate(total=Sum('purchased_quantity')).annotate(branch_name = ExpressionWrapper(Concat(F("purchase_id__branch_id__city__city_name") , F('purchase_id__branch_id__number')) , output_field=models.CharField(max_length=100))).annotate(product_name = ExpressionWrapper(F("product_id__product_name") , output_field=models.CharField(max_length=100))).order_by("-total")
            res = calcBranchesProductsQuantities(statistics)
            if(statistics):
                return(Response(res))
            else:
                return(Response([]))
        else: 
            return Response({"year" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    elif day:
        if validate_date_format(day):
            statistics = statistics.filter(purchase_id__date_of_purchase__year = day.split('-')[0] ,purchase_id__date_of_purchase__day = day.split('-')[2] , purchase_id__date_of_purchase__month = day.split('-')[1])
            statistics=statistics.values('purchase_id__branch_id' , "product_id").annotate(total=Sum('purchased_quantity')).annotate(branch_name = ExpressionWrapper(Concat(F("purchase_id__branch_id__city__city_name") , F('purchase_id__branch_id__number')) , output_field=models.CharField(max_length=100))).annotate(product_name = ExpressionWrapper(F("product_id__product_name") , output_field=models.CharField(max_length=100))).order_by("-total")
            res = calcBranchesProductsQuantities(statistics)
            if(statistics):
                return(Response(res))
            else:
                return(Response([]))
        else: 
            return Response({"day" : "invalid date" }, status=status.HTTP_400_BAD_REQUEST)
    else:
        statistics=statistics.values('purchase_id__branch_id' , "product_id").annotate(total=Sum('purchased_quantity')).annotate(branch_name = ExpressionWrapper(Concat(F("purchase_id__branch_id__city__city_name") , F('purchase_id__branch_id__number')) , output_field=models.CharField(max_length=100))).annotate(product_name = ExpressionWrapper(F("product_id__product_name") , output_field=models.CharField(max_length=100))).order_by("-total")
        res = calcBranchesProductsQuantities(statistics)
        if(statistics):
            return(Response(res))
        else:
            return(Response([]))
 

# @api_view(['GET','post'])
# def hello(request):
#      rule=generate_association_rules_df()
#      save_association_rules(rule)
#      return Response({"message":"hello"})

