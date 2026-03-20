from django.urls import path
from . import views
from .views import apply_coupon

app_name = "orders"

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.order_success, name='order_success'),
    path('history/', views.order_history, name='order_history'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('apply-coupon/', apply_coupon, name='apply_coupon'),
    path("remove-coupon/", views.remove_coupon, name="remove_coupon"),
    path("order/<int:order_id>/", views.order_detail, name="order_detail"),
    path("payment/<int:order_id>/", views.payment_page, name="payment_page"),
    path("confirm-payment/<int:order_id>/", views.confirm_payment, name="confirm_payment"),
]