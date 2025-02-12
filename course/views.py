from decimal import Decimal
from django.shortcuts import redirect,get_object_or_404
from sslcommerz_lib import SSLCOMMERZ 
from rest_framework import generics,viewsets,status,views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from user.models import User
from course import models as course_model
from .validators import generate_transaction_id
from course import serializers as course_serializer

# Create your views here.
class CategoryView(generics.ListAPIView):
    queryset = course_model.Category.objects.filter(active=True)
    serializer_class = course_serializer.CategoriySerializer
    permission_classes = [AllowAny]
class CourseView(generics.ListAPIView):
    queryset = course_model.Course.objects.filter(platform_status='Published',teacher_course_status='Published')
    serializer_class = course_serializer.CourseSerializer
    permission_classes = [AllowAny]
    
class CourseDetailView(generics.RetrieveAPIView):
    serializer_class = course_serializer.CourseSerializer
    permission_classes = [AllowAny]
    def get_object(self):
        slug = self.kwargs['slug']
        course = course_model.Course.objects.get(slug=slug)
        return course

class CartAPIView(generics.ListCreateAPIView):
    queryset = course_model.Cart.objects.all()
    print("working 1")
    serializer_class = course_serializer.CartSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        print("working2")
        # 1
        course_id = request.data['course_id']
        course = course_model.Course.objects.filter(course_id=course_id).first()
        print(course)
        user_id = request.data['user_id']
        cart_id = request.data['cart_id']
        country = request.data['country']
        # 2
        if user_id != 'undefined':
            user = User.objects.filter(user_id=user_id).first()
        else:
            user = None
        print(user)
        # 3 
        
        if course:
            price = course.price
        else:
            price = 0.00
            
        print(price)
        country = course_model.Country.objects.filter(name=country).first()
        print(country)
        if country:
            tax_rate = country.tax_rate
        else:
            tax_rate = 2
        print(tax_rate)
        
        tax_fee = price * Decimal(tax_rate/100)
        total = price + tax_fee
        print(tax_fee,total)    
        cart = course_model.Cart.objects.filter(cart_id=cart_id,course=course).first()
        if cart:
        # 1
            cart.course = course
            cart.user = user
        # 2
            cart.price = price
        # 3
            cart.tax_fee = tax_fee
        # 4 
            cart.total = total
        # 5 
            cart.cart_id = cart_id
            cart.country = country.name
            
            cart.save()
            
            return Response({"error":"cart updated successfully"},status=status.HTTP_200_OK)
        else:
            cart = course_model.Cart()
            cart.course = course
            cart.user = user
            cart.price = price
            cart.tax_fee = tax_fee
            cart.total = total
            cart.country = country.name
            cart.cart_id = cart_id
            
            cart.save()
            
            return Response({"error":"cart created successfully"},status=status.HTTP_201_CREATED)

class CartListAPIView(generics.ListAPIView):
    serializer_class = course_serializer.CartSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        queryset = course_model.Cart.objects.filter(cart_id=cart_id)
        return queryset

class CartItemDeleteApiView(generics.DestroyAPIView):
    serializer_class = course_serializer.CartSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        cart_id = self.kwargs['cart_id']
        item_id = self.kwargs['item_id']
        course = course_model.Course.objects.filter(course_id=item_id).first()
        return course_model.Cart.objects.filter(cart_id=cart_id,course=course).first()  

class CartDetailAPIView(generics.RetrieveAPIView):
    serializer_class = course_serializer.CartSerializer
    permission_classes = [AllowAny]
    lookup_field = 'cart_id'  
    
    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        queryset = course_model.Cart.objects.filter(cart_id=cart_id)
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        total_price = 0.00
        total_tax = 0.00
        total_total = 0.00
        
        for cart_item in queryset:
            total_price += float(self.calculate_price(cart_item))
            total_tax += float(self.calculate_tax(cart_item))
            total_total += round(float(self.calculate_total(cart_item)),2)
            
        data = {
            "price":total_price,
            "tax": total_tax,
            "total":total_total
        }
        
        return Response({"status":data},status=status.HTTP_200_OK)
            
    def calculate_price(self,cart_item):
        return cart_item.price
    def calculate_tax(self,cart_item):
        return cart_item.tax_fee
    def calculate_total(self,cart_item):
        return cart_item.total
    
class CreateOrderAPIView(generics.CreateAPIView):
    queryset = course_model.CartOrder.objects.all()
    serializer_class = course_serializer.CartOrderSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        full_name = request.data.get('full_name')
        email = request.data.get('email')
        country = request.data.get('country')
        cart_id = request.data.get('cart_id')
        user_id = request.data.get('user_id')
        phone = request.data.get('phone')

        # Fetch user if user_id is valid
        user = User.objects.filter(user_id=user_id).first()

        # Fetch cart items for the given cart_id
        cart_items = course_model.Cart.objects.filter(cart_id=cart_id)
        if not cart_items.exists():
            return Response({"error": "No items in cart"}, status=status.HTTP_400_BAD_REQUEST)

        # Initialize totals
        total_price = total_tax = total_initial_total = total_total = 0.00

        # Create CartOrder
        order = course_model.CartOrder.objects.create(
            full_name=full_name,
            email=email,
            country=country,
            student=user,
        )

        # Add items to the order
        for cart_item in cart_items:
            course_model.CartOrderItem.objects.create(
                order=order,
                course=cart_item.course,
                price=cart_item.price,
                tax_fee=cart_item.tax_fee,
                total=cart_item.total,
                initial_total=cart_item.total,
                teacher=cart_item.course.teacher,
            )
            total_price += float(cart_item.price)
            total_tax += float(cart_item.tax_fee)
            total_initial_total += float(cart_item.total)
            total_total += float(cart_item.total)

            # # Add teacher to the order
            # if cart_item.course.teacher:
            #     order.teacher.add(cart_item.course.teacher)
            

        # Update totals in the order
        order.sub_total = total_price
        order.tax_fee = total_tax
        order.initial_total = total_initial_total
        order.total = total_total
        order.phone = phone
        order.save()

        # Clear cart after order creation
        cart_items.delete()

        return Response({"message": "Order Created Successfully and deleted from cart","order_oid":order.oid}, status=status.HTTP_201_CREATED)

class StudentOrderAPIView(generics.ListAPIView):
    queryset = course_model.CartOrder.objects.all()
    serializer_class = course_serializer.CartOrderSerializer
    
    def get_queryset(self):
        print("linked")
        user_id = self.kwargs['user_id']
        print("user_id",user_id)
        if user_id is not None:
            user = User.objects.get(user_id=user_id)
            print(user)
        queryset = course_model.CartOrder.objects.filter(student=user,payment_status='Pending')
        print(queryset)
        return queryset

class CheckoutAPIView(generics.RetrieveAPIView):
    serializer_class = course_serializer.CartOrderSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        oid = self.kwargs.get('oid')
        return get_object_or_404(course_model.CartOrder, oid=oid, payment_status="Pending")
     
     
class CouponAPIView(generics.CreateAPIView):
    serializer_class = course_serializer.CouponSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        order_oid = request.data['order_oid']
        coupon_code = request.data['coupon_code']
        
        order = course_model.CartOrder.objects.get(oid=order_oid)
        coupon = course_model.Coupon.objects.get(code=coupon_code)
        print(order)
        print(coupon)
        
        if coupon:
            order_items = course_model.CartOrderItem.objects.filter(order=order,teacher=coupon.teacher)
            print(order_items)
            for o in order_items:
                print(o)
                print(o.coupons)
                if not coupon in o.coupons.all():
                    discount = o.total * coupon.discount /100
                    o.total -= discount
                    o.price -= discount
                    o.saved += discount
                    o.coupons.add(coupon)
                    o.applied_coupon = True
                    
                    order.coupons.add(coupon)
                    order.total -= discount
                    order.sub_total -= discount
                    order.saved += discount
                    
                    o.save()
                    order.save()
                    coupon.used_by.add(order.student)
                    return Response({"message":"Coupon found and activated"},status=status.HTTP_201_CREATED)
                else:
                    return Response({"message":"Coupon Already Applied"},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message":"Coupon not found"},status=status.HTTP_404_NOT_FOUND)
        
class PaymentWithSSLCommerz(generics.CreateAPIView):
    serializer_class = course_serializer.CartOrderSerializer
    queryset = course_model.CartOrder.objects.all()

    def create(self, request, *args, **kwargs):
        order_oid = request.data.get('order_oid')
        user_id = request.data.get('user_id')
        print("Order OID:", order_oid)
        print(user_id)
        try:
            order = course_model.CartOrder.objects.get(oid=order_oid)
            print("Order:", order)
        except course_model.CartOrder.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            settings = {
                'store_id': 'selfl67a74174e7dfc', 
                'store_pass': 'selfl67a74174e7dfc@ssl', 
                'issandbox': True 
            }
            sslcz = SSLCOMMERZ(settings)
            transaction_id = generate_transaction_id()
            post_body = {
                'total_amount': order.total,  
                'currency': "BDT", 
                'tran_id': transaction_id, 
                'success_url': f"http://127.0.0.1:8000/api/v1/order/payment/sslcommerz/confirmation/{order_oid}/{transaction_id}/",
                'fail_url': "http://127.0.0.1:8000/api/v1/order/payment/sslcommerz/fail/", 
                'cancel_url': "http://localhost:5173/payment/cancel/", 
                'emi_option': 0,
                'cus_name': order.full_name,
                'cus_email': order.email,
                'cus_phone': order.phone, 
                'cus_add1': "dhaka",  
                'cus_city': "city", 
                'cus_country': order.country,
                'cus_postcode': "1212",  
                'shipping_method': "NO", 
                'product_name': "Order", 
                'product_category': "General", 
                'product_profile': "general",
             }
            response = sslcz.createSession(post_body)
            print("SSLCommerz Response:", response)
            if response['status'] == 'SUCCESS':
                return Response({"redirect_url": response['GatewayPageURL']}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Payment initiation failed"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error: {e}")
            return Response({"message": "Something went wrong while trying to make payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentConfirm(views.APIView):
    serializer_class = course_serializer.CartOrderSerializer
    queryset = course_model.CartOrder.objects.all()

    def post(self, request, order_oid, transaction_id):
        try:
            order = course_model.CartOrder.objects.get(oid=order_oid)
            order.payment_status = 'Paid'
            
            order.save()
            order_items = course_model.CartOrderItem.objects.filter(order=order)
            for o in order_items:
                course_model.EnrolledCourse.objects.create(
                    course=o.course,
                    user=order.student,
                    teacher=o.teacher,
                    order_item=o
                )
            print("Order:", order)
        except course_model.CartOrder.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Return JSON response with redirect URL
        return redirect(f"http://localhost:5173/payment/success/{transaction_id}/")
class PaymentFail(views.APIView):
    serializer_class = course_serializer.CartOrderSerializer
    queryset = course_model.CartOrder.objects.all()

    def post(self,request):
        return redirect(f"http://localhost:5173/payment/fail/")
 
    
class ReviewView(viewsets.ModelViewSet):
    serializer_class = course_serializer.ReviewSerializer
    queryset = course_model.Review.objects.all()


class BlogAPIView(viewsets.ModelViewSet):
    serializer_class = course_serializer.BlogSerializer
    queryset = course_model.Blog.objects.all()


