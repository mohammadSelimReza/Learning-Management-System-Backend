from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from course import models as course_model
from user import serializers as model_serializer




class CategoriySerializer(serializers.ModelSerializer):
    class Meta:
        model = course_model.Category
        fields = ["title", "image", "slug", "course_count"]

class VariantItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = course_model.VariantItem
        fields = "__all__"

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = course_model.Cart
        fields = [
                "course",
                "user",
                "price",
                "tax_fee",
                "total",
                "country",
                "cart_no",
                "cart_id",
        ]
    def __init__(self,*args,**kwargs):
        super(CartSerializer,self).__init__(*args,**kwargs)
        response = self.context.get("request")
        if response and response.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3
            
class CartOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = course_model.CartOrderItem
        fields = [
            "order",
            "teacher",
            "course",
            "tax_fee",
            "total",
            "initial_total",
            "saved",
            "coupons",
            "applied_coupon",
            "oid",
            "date",
            "order_id",
            "payment_status",
        ]
    def __init__(self,*args,**kwargs):
        super(CartOrderItemSerializer,self).__init__(*args,**kwargs)
        response = self.context.get("request")
        if response and response.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3

class CartOrderSerializer(serializers.ModelSerializer):
    order_items = CartOrderItemSerializer(many=True)

    class Meta:
        model = course_model.CartOrder
        fields = [
            "teacher",
            "student",
            "price",
            "sub_total",
            "tax_fee",
            "initial_total",
            "saved",
            "total",
            "phone",
            "payment_status",
            "full_name",
            "email",
            "country",
            "coupons",
            "strip_session_id",
            "oid",
            "date",
            "order_items",
        ]

    def __init__(self,*args,**kwargs):
        super(CartOrderSerializer,self).__init__(*args,**kwargs)
        response = self.context.get("request")
        if response and response.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3
            
class ReviewSerializer(serializers.ModelSerializer):
    profile = model_serializer.ProfileSerializer()
    class Meta:
        model = course_model.Review
        fields = [
            'user',
            'course',
            'review',
            'rating',
            'repy',
            'review_id',
            'date',
            'profile',
        ]

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = course_model.Coupon
        fields = "__all__"
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = course_model.Country
        fields = "__all__"
class VariantSerializer(serializers.ModelSerializer):
    variant_items = VariantItemSerializer(many=True)

    class Meta:
        model = course_model.Variant
        fields = [
            "course",
            "title",
            "varient_id",
            "date",
            "variant_items",
        ]

class EnrolledCourseSerializer(serializers.ModelSerializer):
    # lectures = VariantItemSerializer(many=True)
    # carriculam = VariantItemSerializer(many=True)
    # review = ReviewSerializer(many=True, read_only=True)
    lectures = VariantItemSerializer(many=True)
    carriculam = VariantSerializer(many=True)
    review = ReviewSerializer(many=False)
    class Meta:
        model = course_model.EnrolledCourse
        fields = [
            "course",
            "user",
            "teacher",
            "order_item",
            "enrolled_id",
            "date",
            "lectures",
            "carriculam",
            "review",
        ]
    def __init__(self,*args,**kwargs):
        super(EnrolledCourseSerializer,self).__init__(*args,**kwargs)
        response = self.context.get("request")
        if response and response.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3
            
class CourseSerializer(serializers.ModelSerializer):
    students = EnrolledCourseSerializer(many=True)
    curriculum = VariantSerializer(many=True)
    lectures = VariantItemSerializer(many=True)
    reviews = ReviewSerializer(many=True)
    class Meta:
        model = course_model.Course
        fields = [
            "teacher",
            "category",
            "file",
            "image",
            "title",
            "info",
            "price",
            "language",
            "level",
            "platform_status",
            "teacher_course_status",
            "featured",
            "course_id",
            "slug",
            "date",
            "students",
            "curriculum",
            "lectures",
            "average_rating",
            "reviews",
            "rating_count",
        ]
    def __init__(self,*args,**kwargs):
        super(CourseSerializer,self).__init__(*args,**kwargs)
        response = self.context.get("request")
        if response and response.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = course_model.Blog
        fields = [
            "title",
            "blog_img",
            "blog_text",
            "slug",
        ]