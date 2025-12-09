from django.db import models
from django.contrib.auth.models import AbstractUser

# User model
class User(AbstractUser):
    ROLE_CHOICES = (('admin', 'Admin'), ('annotator', 'Annotator'))
    STATUS_CHOICES = (('active', 'Active'), ('warning', 'Warning'), ('banned', 'Banned'))
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='annotator')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    balance_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

# Image task model
class Image(models.Model):
    REVIEW_STATUS_CHOICES = (('none', 'None'), ('pending', 'Pending'), ('reviewed', 'Reviewed'))
    STATUS_CHOICES = (('active', 'Active'), ('completed', 'Completed'))

    image_url = models.TextField()  # can be URL or base64
    category_options = models.CharField(max_length=255)  # like "Cat,Dog,Bird"
    final_label = models.CharField(max_length=50, null=True, blank=True)
    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='none')
    bounty = models.DecimalField(max_digits=10, decimal_places=2, default=0.50)
    assigned_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['status', 'assigned_count'])]

# Payment record model
class Payment(models.Model):
    annotator = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

# Annotation model
class Annotation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    submitted_label = models.CharField(max_length=50)
    is_correct = models.BooleanField(null=True, default=None)  # None=pending, True=correct, False=wrong
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'image')  # one user can only annotate one image once