from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, Coupon


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        'product',
        'variant',
        'quantity',
        'price',
        'item_total',
    )

    def item_total(self, obj):
        if obj.price and obj.quantity:
            return obj.price * obj.quantity
        return 0

    item_total.short_description = "Total"


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'total_amount',
        'payment_method',
        'payment_status',
        'status',
        'created_at',
        'is_shipped',
    )

    # Keep status editable normally
    list_editable = ('payment_status', 'status')

    list_filter = ('status', 'payment_status')
    search_fields = ('user__username', 'id', 'full_name', 'city')

    inlines = [OrderItemInline]

    readonly_fields = (
        'user',
        'shipping_address_display',
        'total_amount',
        'payment_method',
        'created_at',
    )

    fieldsets = (
        ("Customer Information", {
            "fields": (
                'user',
                'shipping_address_display',
            )
        }),
        ("Payment Information", {
            "fields": (
                'payment_method',
                'payment_status',
            )
        }),
        ("Order Information", {
            "fields": (
                'total_amount',
                'status',
                'created_at',
            )
        }),
        ("Shipping & Tracking", {
            "fields": (
                'tracking_id',
                'is_shipped',
            )
        }),
    )

    def shipping_address_display(self, obj):
        return format_html(
            "<strong>{}</strong><br>"
            "{}<br>"
            "{} - {}<br>"
            "Phone: {}",
            obj.full_name,
            obj.address,
            obj.city,
            obj.postal_code,
            obj.phone,
        )

    shipping_address_display.short_description = "Shipping Address"

    # 🔒 Lock status in detail page if Cancelled
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)

        if obj and obj.status == "Cancelled":
            readonly.append('status')

        return readonly

    # 🔒 Lock status in detail save
    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Order.objects.get(pk=obj.pk)

            if old_obj.status == "Cancelled":
                obj.status = "Cancelled"

        super().save_model(request, obj, form, change)

    # 🔒 Lock status in list view editing
    def get_changelist_formset(self, request, **kwargs):
        formset = super().get_changelist_formset(request, **kwargs)

        class CustomFormset(formset):
            def clean(self_inner):
                super().clean()

                for form in self_inner.forms:
                    if form.instance.pk:
                        old_status = Order.objects.get(pk=form.instance.pk).status

                        if old_status == "Cancelled":
                            form.cleaned_data["status"] = "Cancelled"

        return CustomFormset

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "discount",
        "active",
        "valid_from",
        "valid_to"
    )

    list_filter = (
        "active",
        "valid_from",
        "valid_to"
    )

    search_fields = (
        "code",
    )

    ordering = (
        "-valid_from",
    )
admin.site.register(Order, OrderAdmin)