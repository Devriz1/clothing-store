from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import Address, PaymentMethod

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # Columns shown in user list
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
        "is_staff",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
    )

    # 🔥 This is the important part
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {
            "fields": (
                "first_name",
                "last_name",
                "email",
                "phone",
                "shipping_address",
            )
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        ("Important dates", {
            "fields": ("last_login", "date_joined"),
        }),
    )
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "is_default")
    list_filter = ("city",)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("user", "payment_type", "is_default")