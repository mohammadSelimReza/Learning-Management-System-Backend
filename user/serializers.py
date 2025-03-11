from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from user import models as user_model


class MyTokenPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["full_name"] = user.full_name
        token["username"] = user.username
        token["user_id"] = user.user_id
        token['email'] = user.email
        token['user_type'] = user.profile.user_type
        token['image'] =user.profile.image
        return token
  
  
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_model.User
        fields = "__all__"
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_model.Profile
        fields = "__all__"

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_model.Teacher
        fields = ['id','user']
    
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password],style={'input_type': 'password'}
    )
    password2 = serializers.CharField(write_only=True, required=True,style={'input_type': 'password'})
    class Meta:
        model = user_model.User
        fields = ["full_name", "email", "password", "password2"]
    
    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match"}
            )
        return attrs
    def create(self, validated_data):
        validated_data.pop("password2")
        user = user_model.User.objects.create(
            full_name=validated_data["full_name"],
            email=validated_data["email"],
        )
        email_username, _ = user.email.split("@")
        user.username = email_username
        user.set_password(validated_data["password"])
        user.is_active = False
        user.save()
        return user
    
    
