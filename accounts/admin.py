from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import Address, PaymentMethod
import csv
from django.http import HttpResponse
from django.urls import path


@admin.register(User)
class CustomUserAdmin(UserAdmin):

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

    # ✅ ADD THIS
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'export-csv/',
                self.admin_site.admin_view(self.export_csv)
            ),
        ]
        return custom_urls + urls

    def export_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=customers.csv'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Email'])

        users = User.objects.all()

        for user in users:
            name = f"{user.first_name} {user.last_name}".strip()
            writer.writerow([
                name if name else user.username,
                user.email
            ])

        return response
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "is_default")
    list_filter = ("city",)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("user", "payment_type", "is_default")