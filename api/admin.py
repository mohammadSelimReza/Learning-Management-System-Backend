from django.contrib import admin

# Register your models here.
from django.contrib import admin
from api.models import (
    Teacher,
    Category,
    Course,
    Variant,
    VariantItem,
    QA,
    QAM,
    Cart,
    CartOrder,
    CartOrderItem,
    Certificate,
    CompletedLesson,
    EnrolledCourse,
    Note,
    Review,
    Notification,
    Coupon,
    Wishlist,
    Country,
)

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "course_count"]


admin.site.register(Teacher)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Course)
admin.site.register(Variant)
admin.site.register(VariantItem)
admin.site.register(QA)
admin.site.register(QAM)
admin.site.register(Cart)
admin.site.register(CartOrder)
admin.site.register(CartOrderItem)
admin.site.register(Certificate)
admin.site.register(CompletedLesson)
admin.site.register(EnrolledCourse)
admin.site.register(Note)
admin.site.register(Review)
admin.site.register(Notification)
admin.site.register(Coupon)
admin.site.register(Wishlist)
admin.site.register(Country)
