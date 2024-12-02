from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render
from django.template.loader import render_to_string
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api import serializers as api_serializer
from api import models as api_model
from user.models import User

from .validators import generate_random_otp
from rest_framework import viewsets

from decimal import Decimal


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


class TeacherView(generics.ListCreateAPIView):
    queryset = api_model.Teacher.objects.all()
    serializer_class = api_serializer.TeacherSerializer
    permission_classes = [AllowAny]


class CategoryView(generics.ListAPIView):
    queryset = api_model.Category.objects.filter(active=True)
    serializer_class = api_serializer.CategoriySerializer
    permission_classes = [AllowAny]


class CourseView(generics.ListAPIView):
    queryset = api_model.Course.objects.filter(
        platform_status="Published", teacher_course_status="Published"
    )
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]


class CourseDetailsAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        slug = self.kwargs["slug"]
        course = api_model.Course.objects.get(
            slug=slug, platform_status="Published", teacher_course_status="Published"
        )
        return course


class CartAPIView(generics.CreateAPIView):
    queryset = api_model.Cart.objects.all()
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        course_id = request.data["course_id"]
        user_id = request.data["user_id"]
        price = request.data["price"]
        cart_id = request.data["cart_id"]
        country = request.data["country"]
        course = api_model.Course.objects.filter(course_id=course_id).first()
        user = None
        if user_id and user_id != "undefined":
            user = User.objects.filter(id=user_id).first()
        try:
            country_object = api_model.Country.objects.filter(name=country).first()
            country = country_object.name
        except:
            country_object = None
            country = "USA"
        if country_object:
            tax_rate = country_object.tax_rate / 100
        else:
            tax_rate = 5

        cart = api_model.Cart.objects.filter(cart_id=cart_id, course=course).first()
        print(cart)
        if cart:
            cart.course = course
            cart.user = user
            cart.price = price
            cart.tax_rate = Decimal(price) * Decimal(tax_rate)
            cart.country = country
            cart.total = Decimal(cart.price) + Decimal(tax_rate)
            cart.save()

            return Response(
                {"message": "Cart Successfully Added"}, status=status.HTTP_200_OK
            )
        else:
            cart = api_model.Cart()
            cart.course = course
            cart.user = user
            cart.price = price
            cart.tax_rate = Decimal(price) * Decimal(tax_rate)
            cart.country = country
            cart.total = Decimal(cart.price) + Decimal(tax_rate)
            cart.save()

            return Response(
                {"message": "Cart Created Added"}, status=status.HTTP_201_CREATED
            )


class VariantView(generics.ListAPIView):
    queryset = api_model.Variant.objects.all()
    serializer_class = api_serializer.VariantSerializer
    permission_classes = [AllowAny]


class VariantItemView(generics.ListAPIView):
    queryset = api_model.VariantItem.objects.all()
    serializer_class = api_serializer.VariantItemSerializer
    permission_classes = [AllowAny]
