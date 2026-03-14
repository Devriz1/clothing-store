from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    shipping_address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username
    
class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses"  # 👈 ADD THIS
    )
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_line = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user).update(is_default=False)
        super().save(*args, **kwargs)
    
class PaymentMethod(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payment_methods"
    )

    PAYMENT_TYPES = (
        ("CARD", "Card"),
        ("UPI", "UPI"),
        ("COD", "Cash on Delivery"),
    )

    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES)
    provider_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=100, blank=True)

    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.payment_type} - {self.user.username}"