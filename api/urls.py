from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import routers
from api import views as api_views
from django.urls import include, path

router = routers.DefaultRouter()

# router.register(r"teacher", api_views.TeacherView, basename="teacherView")

urlpatterns = [
    path("user/token/", api_views.MyTokenObtainPairView.as_view(), name="token"),
    path("user/token/refresh/", TokenRefreshView.as_view(), name="refreshToken"),
    path("user/registration/", api_views.RegisterView.as_view(), name="registration"),
    path(
        "user/password-reset/<email>/",
        api_views.ResetPasswordView.as_view(),
        name="passwordReset",
    ),
    path(
        "user/password-change/",
        api_views.PasswordChangeAPIView.as_view(),
        name="passwordChange",
    ),
    path('course/category/',api_views.CategoryView.as_view(),name='categoryView'),
    path('course/course/',api_views.CourseView.as_view(),name='courseView'),
    path("course/search/",api_views.SearchCourseAPIView.as_view(),name='newOrder'),
    path('course/course/<slug>',api_views.CourseDetailView.as_view(),name='courseView'),
    path('course/cart/add/',api_views.CartAPIView.as_view(),name='courseView'),
    path('course/cart/<cart_id>/',api_views.CartListAPIView.as_view(),name='courseView'),
    path('course/cart/stat/<cart_id>/',api_views.CartDetailAPIView.as_view(),name='courseView'),
    path('course/cart/<cart_id>/<item_id>/',api_views.CartItemDeleteApiView.as_view(),name='courseView'),
    path("order/create-order/",api_views.CreateOrderAPIView.as_view(),name='newOrder'),
    path("order/checkout/<oid>/",api_views.CheckoutAPIView.as_view(),name='newOrder'),
    path("order/coupon/",api_views.CouponAPIView.as_view(),name='newOrder'),
    path("payment/stripe-checkout/<order_oid>/",api_views.StripeCheckoutAPIView.as_view(),name='newOrder'),
    path("payment/payment-success/",api_views.PaymentSuccessAPIView.as_view(),name='newOrder'),
    
]
