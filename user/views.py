from django.shortcuts import render,redirect,get_object_or_404
from rest_framework import generics,status,viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from user import serializers as user_serializer
from user import models as user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .validators import generate_random_otp
# Create your views here.
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = user_serializer.MyTokenPairSerializer
    permission_classes = [AllowAny]
    
class RegistrationAPIView(generics.CreateAPIView):
    queryset = user_model.User.objects.all()
    serializer_class = user_serializer.RegistrationSerializer
    
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # 
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # 
            confirm_link = f"https://edusoft-three.vercel.app/api/v1/user/activate/{uid}/{token}"
            email_subject = "Confirm your mail"
            email_body = render_to_string('confirm_email.html',{'confirm_link':confirm_link})
            email = EmailMultiAlternatives(email_subject,'',to=[user.email])
            email.attach_alternative(email_body,'text/html')
            # 
            email.send()
            
            return Response({"detail":"Check your mail to activate your account"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

def activate_account(request,uid64,token):
    print("uid64",uid64)
    print("token:",token)
    try:
        uid = force_str(urlsafe_base64_decode(uid64))
        print("uid",uid)
        user = user_model.User.objects.get(user_id=uid)
        print("user",user)
    except:
        user = None
    if user is not None:
        user.is_active =True
        user.save()
        return redirect(f"https://edusoft-lms.netlify.app/login")
    return redirect(f"https://edusoft-lms.netlify.app")

class ResetPasswordView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = user_serializer.UserSerializer

    def get_object(self):
        email = self.kwargs["email"]
        user = user_model.User.objects.filter(email=email).first()
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
    serializer_class = user_serializer.UserSerializer

    def create(self, request, *args, **kwargs):
        otp = request.data["otp"]
        uuidb64 = request.data["uuidb64"]
        password = request.data["password"]

        user = user_model.User.objects.get(otp=otp, user_id=uuidb64)
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
class PasswordUpdateAPIView(generics.UpdateAPIView):
    """
    API to update user password securely.
    """
   
    serializer_class = user_serializer.UserSerializer

    def update(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        password = request.data.get("password")

        if not password:
            return Response({"message": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(user_model.User, user_id=user_id)
        user.set_password(password)
        user.otp = ""  # Reset OTP (if used for verification)
        user.save()

        return Response({"message": "Password changed successfully"},status=status.HTTP_200_OK)
    
class ProfileUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = user_serializer.ProfileSerializer
    def get_object(self):
        user_id = self.kwargs['user_id']
        user = user_model.User.objects.get(user_id=user_id)
        return user_model.Profile.objects.get(user=user)