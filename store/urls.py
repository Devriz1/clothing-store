from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("terms/", views.terms_conditions, name="terms"),
    path("contact/", views.contact, name="contact"),
]