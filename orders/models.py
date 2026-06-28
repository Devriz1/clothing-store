from django.db import models
from django.conf import settings
from store.models import Product, ProductVariant


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)

    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Discount percentage"
    )

    active = models.BooleanField(default=True)

    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    max_uses = models.PositiveIntegerField(default=100)
    used_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


class Order(models.Model):

    PAYMENT_CHOICES = (
        ('UPI', 'UPI'),
        ('COD', 'Cash on Delivery'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('Processing', 'Processing'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    )

    ORDER_STATUS_CHOICES = (
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)

    # 💰 Pricing
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    # 💳 Payment
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='Processing'
    )

    # 📦 Order tracking
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='Processing'
    )

    tracking_id = models.CharField(max_length=100, blank=True, null=True)
    is_shipped = models.BooleanField(default=False)

    # 🧾 Invoice
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # First save to get ID
        super().save(*args, **kwargs)

        # Generate invoice number AFTER ID exists
        if not self.invoice_number:
            self.invoice_number = f"HL-INV-{self.id:05d}"
            super().save(update_fields=['invoice_number'])

    def __str__(self):
        return f"Order #{self.id}"

    # 🧠 Calculated subtotal (before delivery & discount)
    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",  # ✅ IMPORTANT (used in template)
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    # ✅ FIXED (property for template use)
    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        if self.variant:
            return f"{self.product.name} ({self.variant.size})"
        return self.product.name