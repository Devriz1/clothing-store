from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import User
from cart.models import Cart
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import ShippingAddressForm
from orders.models import Order
from .models import Address, PaymentMethod
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.http import HttpResponse


def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Check passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/register.html')

        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'accounts/register.html')

        # Create user
        User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        return redirect('accounts:login')

    return render(request, 'accounts/register.html')

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('store:home')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('store:home')


@login_required
def profile_view(request):
    user = request.user

    password_form = PasswordChangeForm(user)
    password_success = False
    open_password_modal = False

    if request.method == "POST":

        # Profile update
        if "first_name" in request.POST:
            user.first_name = request.POST.get("first_name")
            user.last_name = request.POST.get("last_name")
            user.phone = request.POST.get("phone")
            user.shipping_address = request.POST.get("shipping_address")
            user.save()
            return redirect("accounts:profile")

        # Password change
        if "old_password" in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            open_password_modal = True

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                password_success = True
                password_form = PasswordChangeForm(user)

    # Orders
    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    # 🔥 CART COUNT LOGIC
    cart_count = 0
    cart = Cart.objects.filter(user=user).first()
    if cart:
        cart_count = cart.items.count()

    return render(request, "accounts/profile.html", {
        "password_form": password_form,
        "password_success": password_success,
        "open_password_modal": open_password_modal,
        "addresses": user.addresses.all(),
        "payment_methods": user.payment_methods.all(),
        "orders": orders,
        "cart_count": cart_count,   # ✅ ADD THIS
    })


@login_required
def add_address(request):
    if request.method == "POST":
        Address.objects.create(
            user=request.user,
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            address_line=request.POST.get("address_line"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            zip_code=request.POST.get("zip_code"),
            is_default=True if request.POST.get("is_default") else False
        )
        return redirect('/accounts/profile/#addresses')

    return redirect('/accounts/profile/#addresses')

@login_required
def set_default_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)

    Address.objects.filter(user=request.user).update(is_default=False)

    address.is_default = True
    address.save()

    return redirect('/accounts/profile/#addresses')

@login_required
def delete_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)
    address.delete()
    return redirect('/accounts/profile/#addresses')




def create_admin(request):
    User = get_user_model()

    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        return HttpResponse("Admin created!")

    return HttpResponse("Admin already exists")