from user import views as user_view
from course import views as course_view
from django.urls import path,include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
router = routers.DefaultRouter()
# router.register(r"course/review",course_view.ReviewView,basename="review")
router.register(r"blog",course_view.BlogAPIView,basename="blog")
router.register(r"course/action",course_view.CourseActionAPIView,basename="course")
# This app is only created for keeping API endpoint at a place.You will find all URLs of this project in here.
# for models >> go individual app (app: course , app:user )
urlpatterns = [
    path("",include(router.urls)),
    # user management api endpoints:
    path('user/registrations/',user_view.RegistrationAPIView.as_view(),name="create-user"),
    path('user/activate/<uid64>/<token>/',user_view.activate_account,name="confirmation"),
    path('user/token/',user_view.MyTokenObtainPairView.as_view(),name="access_token"),
    path('user/token/refresh/',TokenRefreshView.as_view(),name="refresh_token"),
    path(
        "user/password-reset/<email>/",
        user_view.ResetPasswordView.as_view(),
        name="passwordReset",
    ),
    path(
        "user/password-change/",
        user_view.PasswordChangeAPIView.as_view(),
        name="passwordChange",
    ),
    path(
        "user/profile-upate/<user_id>",
        user_view.ProfileUpdate.as_view(),
        name="profileUpdate",
    ),
    path(
        "user/password-upate/<user_id>",
        user_view.PasswordUpdateAPIView.as_view(),
        name="profileUpdate",
    ),
    # course related all endpoints:
    path('course/category/',course_view.CategoryView.as_view(),name='categoryView'),
    path('course/course/',course_view.CourseView.as_view(),name='courseView'),
    path('course/list/',course_view.CourseCardView.as_view(),name='courseList'),
    path('course/course/<slug>',course_view.CourseDetailView.as_view(),name='courseView'),
    path('course/enrollment/',course_view.EnrollmentAPIView.as_view(),name='enroll'),
    path('course/cart/add/',course_view.CartAPIView.as_view(),name='courseView'),
    path('course/cart/<cart_id>/',course_view.CartListAPIView.as_view(),name='courseView'),
    path('course/cart/stat/<cart_id>/',course_view.CartDetailAPIView.as_view(),name='courseView'),
    path('course/cart/<cart_id>/<item_id>/',course_view.CartItemDeleteApiView.as_view(),name='courseView'),
    path('course/review/',course_view.ReviewView.as_view(),name='reivew'),
    # order based endpoints:
    path("order/create-order/",course_view.CreateOrderAPIView.as_view(),name='newOrder'),
    path("order/check-order/<user_id>",course_view.StudentOrderAPIView.as_view(),name='newOrder'),
    path("order/checkout/<oid>/",course_view.CheckoutAPIView.as_view(),name='newOrder'),
    path("order/coupon/",course_view.CouponAPIView.as_view(),name='newOrder'),
    # payment based endpoint
    path("order/payment/sslcommerz/",course_view.PaymentWithSSLCommerz.as_view(),name="sslcommerz"),
    path("order/payment/sslcommerz/confirmation/<order_oid>/<transaction_id>/",course_view.PaymentConfirm.as_view(), name="sslcommerz_confirmation"),
    path("order/payment/sslcommerz/fail/",course_view.PaymentFail.as_view(), name="sslcommerz_confirmation"),
    path("teacher/info/<user_id>/",user_view.TeacherInfo.as_view(),name="teacherInfo"),
    path("teacher/summary/<teacher_id>/",course_view.TeacherSummaryAPIView.as_view(),name="teacherSummary"),
    path("teacher/course/list/<id>/",user_view.TeacherCourseList.as_view(),name="teacherCourseList"),
    path("teacher/best/course/<teacher_id>/",course_view.TeacherBestSellingCourseAPIView.as_view({'get':'list'}),name="bestSales"),
     
]





