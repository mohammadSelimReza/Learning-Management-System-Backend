from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from shortuuid.django_fields import ShortUUIDField




# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True, blank=True,default="username")
    email = models.EmailField(max_length=255, unique=True,default="email")
    full_name = models.CharField(max_length=255, blank=True,default="full_name")
    otp = models.CharField(max_length=6, null=True, blank=True, default="123456")
    refresh = models.CharField(max_length=255, null=True, blank=True, default="x")
    user_id = ShortUUIDField(
        length=6, max_length=6, alphabet="0123456789", primary_key=True
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        email_username, _ = self.email.split("@")
        if self.full_name == "" or self.full_name == None or self.full_name=="full_name":
            self.full_name = email_username
        if self.username == "" or self.username == None or self.username == "username":
            self.username = email_username

        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_name
    
class Profile(models.Model):
    user = models.OneToOneField(User,related_name="profile", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255,blank=True,null=True,default="me")
    about = models.CharField(max_length=255,blank=True,null=True,default="me")
    image = models.URLField(default="default.jpg", blank=True)
    address = models.TextField(max_length=255,blank=True,null=True,default="me")
    city = models.CharField(max_length=255,blank=True,null=True,default="me")
    country = models.CharField(max_length=255,blank=True,null=True,default="me")
    date = models.DateTimeField(auto_now_add=True)
    user_type = models.CharField(max_length=255,blank=True,null=True,default="Student")
    def __str__(self):
        if self.full_name:
            return str(self.full_name)
        else:
            return str(self.user.full_name)

    def save(self, *args, **kwargs):
        if self.full_name == "" or self.full_name == None or self.full_name == "me" :
            self.full_name = self.user.full_name

        super(Profile, self).save(*args, **kwargs)
        

class Teacher(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.URLField( blank=True, null=True)
    full_name = models.CharField(max_length=40, blank=True, null=True)
    bio = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    linkedIn = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    country = models.CharField(blank=True, null=True, max_length=50)
    user_type = models.CharField(max_length=255,default="Teacher")
    def __str__(self):
        if self.full_name:
            return self.full_name
        else:
            return self.user.full_name    
        
# 

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)