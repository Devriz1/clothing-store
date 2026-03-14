from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "accounts"

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path("add-address/", views.add_address, name="add_address"),
    path("set-default/<int:id>/", views.set_default_address, name="set_default_address"),
    path("delete-address/<int:id>/", views.delete_address, name="delete_address"),
    
]