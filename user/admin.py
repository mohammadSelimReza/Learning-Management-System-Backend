from django.contrib import admin

from .models import Profile, User


# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "full_name", "date"]


class UserAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email"]


admin.site.register(Profile, ProfileAdmin)
admin.site.register(User, UserAdmin)
