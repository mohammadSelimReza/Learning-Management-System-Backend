from decimal import Decimal

import requests
import stripe
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api import models as api_model
from api import serializers as api_serializer
from user.models import User

from .validators import generate_random_otp

stripe.api_key=settings.STRIPE_SECRET_KEY


# Create your views here.
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializer.MyTOkenPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = api_serializer.RegistrationSerializer


class ResetPasswordView(generics.RetrieveAPIView):
    print("called")
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer

    def get_object(self):
        email = self.kwargs["email"]
        user = User.objects.filter(email=email).first()
        if user:
            user.otp = generate_random_otp()
            uuidb64 = user.pk
            refresh = RefreshToken.for_user(user)
            refreshToken = str(refresh.access_token)
            user.refresh = refreshToken
            user.save()
            link = f"http://localhost:5173/create-new-password/?otp={user.otp}&uuidb64={uuidb64}&refresh={refreshToken}"
            merge_data = {
                "link": link,
                "username": user.username,
            }
            subject = "Password Reset Email"
            text_body = render_to_string("email/password_reset.txt", merge_data)
            html_body = render_to_string("email/password_reset.html", merge_data)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email="srreza1999@gmail.com",
                to=[user.email],
            )
            email.attach_alternative(html_body, "text/html")
            email.send()

            print("___link:", link)
        return user


class PasswordChangeAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer

    def create(self, request, *args, **kwargs):
        otp = request.data["otp"]
        uuidb64 = request.data["uuidb64"]
        password = request.data["password"]

        user = User.objects.get(otp=otp, id=uuidb64)
        if user:
            user.set_password(password)
            user.otp = ""
            user.save()
            return Response(
                {"message": "Password Change Successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": "User doesn't exist"}, status=status.HTTP_404_NOT_FOUND
            )


# 

class CategoryView(generics.ListAPIView):
    queryset = api_model.Category.objects.filter(active=True)
    serializer_class = api_serializer.CategoriySerializer
    permission_classes = [AllowAny]
    
class CourseView(generics.ListAPIView):
    queryset = api_model.Course.objects.filter(platform_status='Published',teacher_course_status='Published')
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]

class CourseDetailView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]
    def get_object(self):
        slug = self.kwargs['slug']
        course = api_model.Course.objects.get(slug=slug)
        return course
    
class CartAPIView(generics.ListCreateAPIView):
    queryset = api_model.Cart.objects.all()
    print("working 1")
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        print("working2")
        # 1
        course_id = request.data['course_id']
        course = api_model.Course.objects.filter(course_id=course_id).first()
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
        country = api_model.Country.objects.filter(name=country).first()
        print(country)
        if country:
            tax_rate = country.tax_rate
        else:
            tax_rate = 2
        print(tax_rate)
        
        tax_fee = price * Decimal(tax_rate/100)
        total = price + tax_fee
        print(tax_fee,total)    
        cart = api_model.Cart.objects.filter(cart_id=cart_id,course=course).first()
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
            cart = api_model.Cart()
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
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        queryset = api_model.Cart.objects.filter(cart_id=cart_id)
        return queryset
    
class CartItemDeleteApiView(generics.DestroyAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        cart_id = self.kwargs['cart_id']
        item_id = self.kwargs['item_id']
        course = api_model.Course.objects.filter(course_id=item_id).first()
        return api_model.Cart.objects.filter(cart_id=cart_id,course=course).first()  
    
class CartDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]
    lookup_field = 'cart_id'  
    
    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        queryset = api_model.Cart.objects.filter(cart_id=cart_id)
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
    queryset = api_model.CartOrder.objects.all()
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        full_name = request.data.get('full_name')
        email = request.data.get('email')
        country = request.data.get('country')
        cart_id = request.data.get('cart_id')
        user_id = request.data.get('user_id')

        # Fetch user if user_id is valid
        user = User.objects.filter(user_id=user_id).first()

        # Fetch cart items for the given cart_id
        cart_items = api_model.Cart.objects.filter(cart_id=cart_id)
        if not cart_items.exists():
            return Response({"error": "No items in cart"}, status=status.HTTP_400_BAD_REQUEST)

        # Initialize totals
        total_price = total_tax = total_initial_total = total_total = 0.00

        # Create CartOrder
        order = api_model.CartOrder.objects.create(
            full_name=full_name,
            email=email,
            country=country,
            student=user,
        )

        # Add items to the order
        for cart_item in cart_items:
            api_model.CartOrderItem.objects.create(
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
        order.save()

        # Optional: Clear cart after order creation
        cart_items.delete()

        return Response({"message": "Order Created Successfully"}, status=status.HTTP_201_CREATED)


class CheckoutAPIView(generics.RetrieveAPIView):
     serializer_class = api_serializer.CartOrderSerializer
     permission_classes = [AllowAny]
     queryset = api_model.CartOrder.objects.all()
     lookup_field = 'oid'
     

class CouponAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CouponSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        order_oid = request.data['order_oid']
        coupon_code = request.data['coupon_code']
        
        order = api_model.CartOrder.objects.get(oid=order_oid)
        coupon = api_model.Coupon.objects.get(code=coupon_code)
        print(order)
        print(coupon)
        
        if coupon:
            order_items = api_model.CartOrderItem.objects.filter(order=order,teacher=coupon.teacher)
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
        
        
        
        
class StripeCheckoutAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        order_oid = self.kwargs['order_oid']
        order = api_model.CartOrder.objects.get(oid=order_oid)
        
        if not order:
            return Response({"message":"Order not found"},status=status.HTTP_404_NOT_FOUND)
        
        try:
            checkout_session= stripe.checkout.Session.create(
                customer_email = order.email,
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data':{
                            'currency':'usd',
                            'product_data':{
                                'name':order.full_name,
                            },
                            'unit_amount':int(order.total*100),
                        },
                        'quantity':1,
                    }
                ],
                mode='payment',
                success_url=settings.FRONTEND_SUCCESS_URL + '/payment-success/' + order.oid + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=settings.FRONTEND_SUCCESS_URL + '/payment-failed/',
                
            )
            print("ck",checkout_session)
            order.strip_session_id = checkout_session.id
            return redirect(checkout_session.url)
        except:
            return Response({"message":"Something went wrong while try to make payment"},status=status.HTTP_404_NOT_FOUND)
        


    

class PaymentSuccessAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    queryset = api_model.CartOrder.objects.all()
    
    def create(self, request, *args, **kwargs):
        order_oid = request.data['order_oid']
        session_id = request.data['session_id']

        order = api_model.CartOrder.objects.get(oid=order_oid)
        order_items = api_model.CartOrderItem.objects.filter(order=order)
        # strip payment
        if session_id != 'null':
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                if order.payment_status == 'Processing':
                    order.payment_status = 'Paid'
                    order.save()
                    api_model.Notification.objects.create(user=order.student,order=order,type="Course Enrollment Completed")
                    for o in order_items:
                        api_model.Notification.objects.create(
                            teacher = o.teacher,
                            order=order,
                            order_item=o,
                            type="New Order"
                        )
                        api_model.EnrolledCourse.objects.create(
                            course=o.course,
                            user=order.student,
                            teacher =o.teacher,
                            order_item=o,
                        )
                    return Response({"message":"Payment Successful"})
                else:
                    return Response({"message":"Already Paid"})
            else:
                return Response({"message":"Payment Failed"})
        else:
            return Response({"message":"Stripe Payment Failed"})
        
        
        
        
        
        
        
class SearchCourseAPIView(generics.CreateAPIView):
    serializer_class= api_serializer.CourseSerializer
    permission_classes= [AllowAny]
    
    def get_queryset(self):
        query = self.request.GET.get('query')
        return api_model.Course.objects.filter(title__icontains=query,platform_status='Published',teacher_course_status='Published')