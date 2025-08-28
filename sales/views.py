from django.shortcuts import render
from rest_framework.views import APIView , Response , status
from rest_framework import generics 
from .models import *
from .serializers import *
from django.db.models.deletion import ProtectedError
from rest_framework.decorators import api_view , permission_classes


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
    