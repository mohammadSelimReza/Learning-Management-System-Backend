from django.contrib import admin
from course.models import Blog,Cart,CartOrder,CartOrderItem,Category,Country,Coupon,Course,EnrolledCourse,Variant,VariantItem,Review
# Register your models here.
admin.site.register(Blog)
admin.site.register(Cart)
admin.site.register(CartOrder)
admin.site.register(CartOrderItem)
admin.site.register(Category)
admin.site.register(Country)
admin.site.register(Coupon)
admin.site.register(Course)
admin.site.register(EnrolledCourse)
admin.site.register(Review)
admin.site.register(Variant)
admin.site.register(VariantItem)