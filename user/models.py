from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save


# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True, default="123456")
    refresh = models.CharField(max_length=255, null=True, blank=True, default="x")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        email_username, _ = self.email.split("@")
        if self.full_name == "" or self.full_name == None:
            self.full_name = email_username
        if self.username == "" or self.username == None:
            self.username = email_username

        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_name


class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    image = models.URLField(default="default.jpg", blank=True)
    address = models.TextField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.full_name:
            return str(self.full_name)
        else:
            return str(self.user.full_name)

    def save(self, *args, **kwargs):
        if self.full_name == "" or self.full_name == None:
            self.full_name = self.user.full_name

        super(Profile, self).save(*args, **kwargs)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
