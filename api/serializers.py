from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user.models import Profile, User

from api import models as api_model


# user auth:
class MyTOkenPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["full_name"] = user.full_name
        token["username"] = user.username
        token["email"] = user.email
        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "full_name", "otp", "refresh"]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["user", "full_name", "image", "address", "city", "country"]


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["full_name", "email", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match"}
            )
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            full_name=validated_data["full_name"],
            email=validated_data["email"],
        )
        email_username, _ = user.email.split("@")
        user.username = email_username
        user.set_password(validated_data["password"])
        user.save()
        return user


# Teacher:
class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_model.Teacher
        fields = [
            "user",
            "image",
            "full_name",
            "bio",
            "facebook",
            "linkedIn",
            "website",
            "about",
            "country",
            #
            "students",
            "review",
            "courses",
        ]


class CategoriySerializer(serializers.ModelSerializer):
    class Meta:
        model = api_model.Category
        fields = ["title", "image", "slug", "course_count"]


class VariantItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_model.VariantItem
        fields = "__all__"


class QAMSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_model.QAM
        fields = "__all__"


class QASerializer(serializers.ModelSerializer):
    messages = QAMSerializer(many=True)
    profile = ProfileSerializer(many=False)

    class Meta:
        model = api_model.QA
        fields = [
            "course",
            "question",
            "qa_id",
            "messages",
            "date",
            "profile",
        ]


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_model.Cart
        fields = "__all__"


class CartOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_model.CartOrderItem
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


class CartOrderSerializer(serializers.ModelSerializer):
    order_items = CartOrderItemSerializer(many=True)

    class Meta:
        model = api_model.CartOrder
        fields = [
            "course",
            "question",
            "answer",
            "qa_id",
            "date",
            "teacher",
            "student",
            "sub_total",
            "tax_fee",
            "initial_total",
            "saved",
            "total",
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


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_model.Certificate
        fields = "__all__"


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_model.Note
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)

    class Meta:
        model = api_model.Review
        fields = [
            "user",
            "course",
            "review",
            "rating",
            "repy",
            "active",
            "date",
            "profile",
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_model.Notification
        fields = "__all__"


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_model.Coupon
        fields = "__all__"


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_model.Wishlist
        fields = "__all__"


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = api_model.Country
        fields = "__all__"


class CompletedLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_model.CompletedLesson
        fields = "__all__"


class VariantSerializer(serializers.ModelSerializer):
    variant_items = VariantItemSerializer()

    class Meta:
        model = api_model.Variant
        fields = [
            "course",
            "title",
            "varient_id",
            "date",
            "variant_items",
        ]


class EnrolledCourseSerializer(serializers.ModelSerializer):
    lectures = VariantItemSerializer(many=True, read_only=True)
    completed_lesson = CompletedLessonSerializer(many=True, read_only=True)
    carriculam = VariantItemSerializer(many=True, read_only=True)
    note = NoteSerializer(many=True, read_only=True)
    qam = QAMSerializer(many=True, read_only=True)
    review = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = api_model.EnrolledCourse
        fields = [
            "course",
            "user",
            "teacher",
            "order_item",
            "enrolled_id",
            "date",
            "lectures",
            "completed_lesson",
            "carriculam",
            "note",
            "qam",
            "review",
        ]


class CourseSerializer(serializers.ModelSerializer):
    students = EnrolledCourseSerializer(many=True)
    curriculum = VariantItemSerializer(many=True)
    lectures = VariantItemSerializer(many=True)

    class Meta:
        model = api_model.Course
        fields = [
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
