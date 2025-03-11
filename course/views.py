from decimal import Decimal
from django.shortcuts import redirect,get_object_or_404
from sslcommerz_lib import SSLCOMMERZ 
from rest_framework import generics,viewsets,status,views,pagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from user.models import User,Teacher
from course import models as course_model
from .validators import generate_transaction_id
from course import serializers as course_serializer
from _backend.settings.base import FRONTEND_URL,BACKEND_URL
from django.db.models import Count
from django.core.cache import cache
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.
class CategoryView(generics.ListAPIView):
    serializer_class = course_serializer.CategoriySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        cache_key = "category_list"

        # Try to get cached serialized data
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data  # Already serialized, no DB or serialization cost

        # Optimized Query: Precompute course_count using annotate()
        queryset = course_model.Category.objects.filter(active=True).annotate(
            course_count=Count("course")
        )

        # Serialize and store in cache
        serialized_data = self.get_serializer(queryset, many=True).data
        cache.set(cache_key, serialized_data, timeout=60 * 20)  # Cache JSON, not queryset

        return serialized_data
        
class CourseView(generics.ListAPIView):
    queryset = course_model.Course.objects.filter(platform_status='Published',teacher_course_status='Published')
    serializer_class = course_serializer.CourseSerializer
    permission_classes = [AllowAny]
    
class CoursePagination(pagination.PageNumberPagination):
    page_size = 9
    page_size_query_param = page_size
    max_page_size = 100
class CourseCardView(generics.ListAPIView): 
    pagination_class = CoursePagination
    serializer_class = course_serializer.CourseCardSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        cache_key = "course_list"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        queryset = (
                        course_model.Course.objects.filter(
                            platform_status="Published", 
                            teacher_course_status="Published", 
                        )
                        .select_related("teacher", "category")
                        .annotate(
                            total_students=Count("enrolled_courses"),
                            total_lessons=Count("variants__variant_items")
                        )
                    )

        # Cache the queryset (store as a list to prevent caching issues)
        cache.set(cache_key, queryset, timeout=60*2)
        return queryset


    
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
                'success_url': f"{BACKEND_URL}/order/payment/sslcommerz/confirmation/{order_oid}/{transaction_id}/",
                'fail_url': f"{BACKEND_URL}/order/payment/sslcommerz/fail/", 
                'cancel_url': f"{FRONTEND_URL}/payment/cancel/", 
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
        return redirect(f"{FRONTEND_URL}/payment/success/{transaction_id}/")
class PaymentFail(views.APIView):
    serializer_class = course_serializer.CartOrderSerializer
    queryset = course_model.CartOrder.objects.all()

    def post(self,request):
        return redirect(f"{FRONTEND_URL}/payment/fail/")
 
    
class ReviewView(generics.ListCreateAPIView):
    serializer_class = course_serializer.ReviewSerializer
    queryset = course_model.Review.objects.all()

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        course_id = request.data.get("course_id")
        review = request.data.get("review")
        rating = request.data.get("rating")
        print("user",user_id)
        print("user",course_id)
        print("user",review)
        print("user",rating)
        # Check and get user
        user = None
        if user_id is not None:
            try:
                user = User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check and get course
        course = None
        if course_id is not None:
            try:
                course = course_model.Course.objects.get(course_id=course_id)
            except course_model.Course.DoesNotExist:
                return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Create the review
        course_model.Review.objects.create(
            user=user,
            course=course,
            review=review,
            rating=rating,
            active=True,
        )
        return Response({"message": "Review has been created"}, status=status.HTTP_201_CREATED)



class BlogAPIView(viewsets.ModelViewSet):
    serializer_class = course_serializer.BlogSerializer
    queryset = course_model.Blog.objects.all()


class EnrollmentAPIView(generics.ListAPIView):
    serializer_class = course_serializer.EnrolledCourseSerializer
    queryset = course_model.EnrolledCourse.objects.all()
    
    
class TeacherSummaryAPIView(generics.ListAPIView):
    serializer_class = course_serializer.TeacherSummarySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        
        try:
            teacher = Teacher.objects.get(id=teacher_id)
        except Teacher.DoesNotExist:
            return []

        one_month_ago = timezone.now() - timedelta(days=28)

        # Aggregate total revenue
        total_courses = course_model.Course.objects.filter(teacher=teacher).count()
        total_revenue = course_model.CartOrderItem.objects.filter(teacher=teacher).aggregate(
            total_revenue=models.Sum("price")
        )["total_revenue"] or 0

        monthly_revenue = course_model.CartOrderItem.objects.filter(teacher=teacher, date__gte=one_month_ago).aggregate(
            monthly_revenue=models.Sum("price")
        )["monthly_revenue"] or 0  # Fixed variable name

        # Optimized student fetching
        enrolled_courses = course_model.EnrolledCourse.objects.filter(teacher=teacher).select_related("user__profile")
        unique_student_ids = set()
        students = []

        for course in enrolled_courses:
            if course.user_id not in unique_student_ids:
                unique_student_ids.add(course.user_id)
                student = {
                    "full_name": course.user.profile.full_name,
                    "image": course.user.profile.image if course.user.profile.image else None,
                    "country": course.user.profile.country,
                    "date": course.date,
                }
                students.append(student)

        return [{
            "total_courses": total_courses,
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue,
            "total_students": len(students),
        }]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class CourseActionAPIView(viewsets.ModelViewSet):
    queryset = course_model.Course.objects.all()
    serializer_class = course_serializer.CourseCreateSerializer
    permission_classes = [AllowAny]


class TeacherBestSellingCourseAPIView(viewsets.ViewSet):
    def list(self, request, teacher_id=None):
        teacher = Teacher.objects.get(id=teacher_id)
        courses_with_total_price = []
        courses = course_model.Course.objects.filter(teacher=teacher)

        for course in courses:
            revenue = course.enrolled_courses.aggregate(total_price=models.Sum('order_item__price'))['total_price'] or 0
            sales = course.enrolled_courses.count()
            courses_with_total_price.append({
                'courses_image': course.image,
                'course_title': course.title,
                'revenue': revenue,
                'sales': sales
            })
        
        # **Sort courses by sales in descending order**
        best_selling_courses = sorted(courses_with_total_price, key=lambda x: x['sales'], reverse=True)

        # **Return only courses that have at least one sale**
        filtered_courses = [course for course in best_selling_courses if course['sales'] > 0]

        return Response(filtered_courses)
    