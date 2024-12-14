from django.db import models

# Create your models here.
import math
from django.db import models
from user.models import User, Profile
from moviepy import VideoFileClip
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
from .constants import (
    LANGUAGE,
    LEVEL,
    PLATFORM_STATUS,
    TEACHER_COURSE_STATUS,
    PAYMENT_STATUS,
    RATING,
    NOTI_TYPE,
)


# Create your models here.
class Teacher(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.FileField(upload_to="teacher", blank=True, null=True)
    full_name = models.CharField(max_length=40, blank=True, null=True)
    bio = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    linkedIn = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    country = models.CharField(blank=True, null=True, max_length=50)

    def __str__(self):
        if self.full_name:
            return self.full_name
        else:
            return self.user.full_name

    def students(self):
        return CartOrderItem.objects.filter(tacher=self)

    def courses(self):
        return Course.objects.filter(taecher=self)

    # didn't find
    def review(self):
        return Review.objects.filter(teacher=self).count()


class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.FileField(upload_to="category", blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Category"
        ordering = [
            "title",
        ]

    def course_count(self):
        return Course.objects.filter(category=self).count()

    def __str__(self):
        return f"Category -> {self.title}"

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)


class Course(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, blank=True, null=True
    )
    file = models.FileField(upload_to="course/file", blank=True, null=True)
    image = models.FileField(upload_to="course/logo", blank=True, null=True)
    title = models.CharField(max_length=100, unique=True)
    info = models.CharField(max_length=200, blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    language = models.CharField(choices=LANGUAGE, max_length=20)
    level = models.CharField(choices=LEVEL, max_length=20)
    platform_status = models.CharField(choices=PLATFORM_STATUS, max_length=20)
    teacher_course_status = models.CharField(
        choices=TEACHER_COURSE_STATUS, max_length=12
    )
    featured = models.BooleanField(default=False)
    course_id = ShortUUIDField(
        length=6, max_length=6, alphabet="0123456789", primary_key=True
    )
    slug = models.SlugField(unique=True, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title)
        super(Course, self).save(*args, **kwargs)

    def __str__(self):
        return f"Course name - {self.title}"

    def students(self):
        return EnrolledCourse.objects.filter(course=self)

    def curriculum(self):
        return VariantItem.objects.filter(variant__course=self)  # noted

    def lectures(self):
        return VariantItem.objects.filter(variant__course=self)  # noted

    def average_rating(self):
        average_rating = Review.objects.filter(course=self).aggregate(
            avg_rating=models.Avg("rating")
        )
        return average_rating["avg_rating"]

    def rating_count(self):
        return Review.objects.filter(course=self).count()

    def reviews(self):
        return Review.objects.filter(course=self, active=True)


class Variant(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=30, unique=True)
    varient_id = ShortUUIDField(
        length=6, max_length=6, alphabet="0123456789", primary_key=True
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def variant_items(self):
        return VariantItem.objects.filter(variant=self)


class VariantItem(models.Model):
    variant = models.ForeignKey(
        Variant, on_delete=models.CASCADE, related_name="variant_items"
    )
    title = models.CharField(max_length=50)
    info = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="varientItem", blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    content_duration = models.CharField(max_length=1000, blank=True, null=True)
    preview = models.BooleanField(default=False)
    variant_item_id = ShortUUIDField(
        length=6, max_length=6, alphabet="0123456789", primary_key=True
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Varient Item => {self.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.file:
            clip = VideoFileClip(self.file.path)
            duration_seconds = clip.duration

            minutes, remainder = divmod(duration_seconds, 60)
            minutes = math.floor(minutes)
            seconds = math.floor(remainder)

            duration_text = f"{minutes}m {seconds}s"

            self.content_duration = duration_text
            super().save(update_fields=["content_duration"])


class QA(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default="annomouse",
    )
    question = models.CharField(max_length=200)
    qa_id = ShortUUIDField(
        length=6, max_length=6, alphabet="0123456789", primary_key=True
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question} by {self.user.full_name}"

    class Meta:
        ordering = ["-date"]

    def profile(self):
        return Profile.objects.filter(user=self.user)

    def messages(self):
        return QAM.objects.filter(question=self)


class QAM(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question = models.ForeignKey(QA, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default="annomouse",
    )
    answer = models.CharField(max_length=200)
    qa_id = ShortUUIDField(
        length=6, max_length=6, alphabet="0123456789", primary_key=True
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.qa_id

class Coupon(models.Model):
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, blank=True, null=True
    )
    used_by = models.ManyToManyField(User, blank=True)
    code = models.CharField(max_length=50)
    discount = models.IntegerField(default=1)
    active = models.BooleanField(default=False)
    date = ShortUUIDField(
        length=6, max_length=6, alphabet="0123456789", primary_key=True
    )

    def __str__(self):
        return self.code
    
class Cart(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    tax_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    country = models.CharField(max_length=50, blank=True, null=True)
    cart_no = ShortUUIDField(
        length=6, max_length=6, alphabet="0123456789", primary_key=True
    )
    cart_id = ShortUUIDField(length=6, max_length=6, alphabet="0123456789")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"cart of {self.user.full_name} for {self.course.title}"


class CartOrder(models.Model):
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True
    )
    student = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    sub_total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    tax_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    initial_total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    saved = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    payment_status = models.CharField(
        choices=PAYMENT_STATUS, max_length=20, default="Pending"
    )
    full_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)

    country = models.CharField(max_length=50, blank=True, null=True)
    coupons = models.ManyToManyField(Coupon, blank=True)
    strip_session_id = models.CharField(max_length=1000, blank=True, null=True)
    oid = ShortUUIDField(
        length=6, max_length=6, alphabet="0123456789", primary_key=True
    )
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.oid

    def order_items(self):
        return CartOrderItem.objects.filter(order=self)


class CartOrderItem(models.Model):
    order = models.ForeignKey(
        CartOrder,
        on_delete=models.CASCADE,
        related_name="orderItem",
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="order_item"
    )
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    tax_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    initial_total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    saved = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    coupons = models.ManyToManyField(Coupon, blank=True)
    applied_coupon = models.BooleanField(default=False)
    oid = ShortUUIDField(
        length=6, max_length=6, alphabet="0123456789", primary_key=True
    )
    date = models.DateTimeField(auto_now_add=True)

    def order_id(self):
        return f"Order Id #{self.order.oid}"

    def payment_status(self):
        return f"{self.order.payment_status}"

    def __str__(self):
        return self.oid


class Certificate(models.Model):
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    certificate_id = ShortUUIDField(
        length=6, max_length=6, alphabet="0123456789", primary_key=True
    )
    issued = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.course.title


class CompletedLesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    variant_item = models.ForeignKey(VariantItem, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.course.title


class EnrolledCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, blank=True, null=True
    )
    order_item = models.ForeignKey(CartOrderItem, on_delete=models.CASCADE)
    enrolled_id = ShortUUIDField(
        length=6, max_length=6, alphabet="0123456789", primary_key=True
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.course.title

    def lectures(self):
        return VariantItem.objects.filter(variant__course=self.course)

    def completed_lesson(self):
        return CompletedLesson.objects.filter(course=self.course, user=self.user)

    def carriculam(self):
        return Variant.objects.filter(course=self.course)

    def note(self):
        return Note.objects.filter(course=self.course, user=self.user)

    def qam(self):
        return QAM.objects.filter(course=self.course)

    def review(self):
        return Review.objects.filter(course=self.course, user=self.user).first()


class Note(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, default="annoymous"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    note = models.TextField(blank=True, null=True)
    note_id = ShortUUIDField(
        length=6, max_length=6, alphabet="0123456789", primary_key=True
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, default="annoymous"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    repy = models.CharField(blank=True, null=True, max_length=1000)
    active = models.BooleanField(default=False)
    date = ShortUUIDField(
        length=6, max_length=6, alphabet="0123456789", primary_key=True
    )

    def __str__(self):
        return self.course.title

    def profile(self):
        return Profile.objects.get(user=self.user)


class Notification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, default="annoymous"
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, blank=True, null=True
    )
    order = models.ForeignKey(
        CartOrder, on_delete=models.SET_NULL, blank=True, null=True
    )
    order_item = models.ForeignKey(
        CartOrderItem, on_delete=models.SET_NULL, blank=True, null=True
    )
    review = models.ForeignKey(Review, on_delete=models.SET_NULL, blank=True, null=True)
    type = models.CharField(max_length=1000, choices=NOTI_TYPE)
    seen = models.BooleanField(default=False)
    date = ShortUUIDField(
        length=6, max_length=6, alphabet="0123456789", primary_key=True
    )

    def __str__(self):
        return self.type





class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} -> {self.course.title}"


class Country(models.Model):
    name = models.CharField(max_length=100)
    tax_rate = models.IntegerField(default=5)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name
