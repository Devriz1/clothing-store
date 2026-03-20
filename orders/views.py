from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Order, OrderItem
from cart.models import CartItem
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404
from accounts.models import Address
from .models import Coupon
from django.utils import timezone
import qrcode
import base64
from io import BytesIO


@login_required
def checkout(request):

    cart = request.user.cart
    cart_items = cart.items.select_related('variant', 'variant__product')

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart:cart_detail')

    total = sum(item.variant.price * item.quantity for item in cart_items)

    # ================= COUPON LOGIC =================

    coupon_id = request.session.get("coupon_id")
    discount = Decimal(0)
    coupon = None

    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)

            # CHECK COUPON USAGE LIMIT
            if coupon.used_count >= coupon.max_uses:
                messages.error(request, "This coupon has reached its usage limit.")
                del request.session["coupon_id"]
                coupon = None
            else:
                discount = (Decimal(total) * coupon.discount) / Decimal(100)

        except Coupon.DoesNotExist:
            discount = Decimal(0)

    subtotal_after_discount = total - discount

    # ================= ADDRESS =================

    addresses = Address.objects.filter(user=request.user)

    if not addresses.exists():
        messages.warning(request, "Please add a delivery address first.")
        return redirect('accounts:add_address')

    default_address = addresses.filter(is_default=True).first()

    if request.method == "POST":

        address_id = request.POST.get("address_id")
        payment_method = request.POST.get("payment_method")

        if not address_id:
            messages.error(request, "Please select a delivery address.")
            return redirect('orders:checkout')

        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            messages.error(request, "Invalid address selected.")
            return redirect('orders:checkout')

        delivery_charge = Decimal(0)
        payment_status = "Processing"

        if payment_method == "COD":
            delivery_charge = Decimal(99)

        final_total = subtotal_after_discount + delivery_charge

        # ================= STOCK CHECK =================

        for item in cart_items:
            if item.quantity > item.variant.stock:
                messages.error(
                    request,
                    f"Not enough stock for {item.variant.product.name} ({item.variant.size})"
                )
                return redirect('cart:cart_detail')

        with transaction.atomic():

            order = Order.objects.create(
                user=request.user,
                full_name=address.full_name,
                address=address.address_line,
                city=address.city,
                postal_code=address.zip_code,
                phone=address.phone,
                total_amount=final_total,
                payment_method=payment_method,
                delivery_charge=delivery_charge,
                payment_status=payment_status,
                coupon=coupon,           # attach coupon
                discount=discount        # store discount amount
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.variant.product,
                    variant=item.variant,
                    price=item.variant.price,
                    quantity=item.quantity
                )

                # reduce stock
                item.variant.stock -= item.quantity
                item.variant.save()

            # increase coupon usage count
            if coupon:
                coupon.used_count += 1
                coupon.save()

            # clear cart
            cart_items.delete()

            # remove coupon from session
            if "coupon_id" in request.session:
                del request.session["coupon_id"]

        if payment_method == "COD":
            order.payment_status = "Pending"
            order.save()
            return redirect('orders:order_success')

        else:
            return redirect('orders:payment_page', order_id=order.id)
    # ================= FINAL TOTAL FOR TEMPLATE =================

    final_total = subtotal_after_discount

    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'discount': discount,
        'final_total': final_total,
        'default_address': default_address,
        'addresses': addresses
    })


@login_required
def order_success(request):
    return render(request, 'orders/order_success.html')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Only allow cancel if Processing
    if order.status == "Processing":

        for item in order.items.all():

            if item.variant:
                item.variant.stock += item.quantity
                item.variant.save()

        order.status = "Cancelled"

        # Only mark refunded if already paid
        if order.payment_status == "Paid":
            order.payment_status = "Refunded"

        order.is_shipped = False
        order.save()

        messages.success(request, "Order cancelled successfully.")

    else:
        messages.warning(request, "This order cannot be cancelled.")

    return redirect('accounts:profile')

def apply_coupon(request):

    if request.method == "POST":

        code = request.POST.get("coupon").strip()

        try:
            coupon = Coupon.objects.get(code__iexact=code, active=True)

            # Check validity date
            if coupon.valid_from <= timezone.now() <= coupon.valid_to:

                # CHECK COUPON USAGE LIMIT
                if coupon.used_count >= coupon.max_uses:
                    messages.error(request, "This coupon has reached its usage limit.")
                    return redirect("orders:checkout")

                # Check if user already used this coupon
                already_used = Order.objects.filter(
                    user=request.user,
                    coupon=coupon
                ).exists()

                if already_used:
                    messages.error(request, "You have already used this coupon.")
                    return redirect("orders:checkout")

                request.session["coupon_id"] = coupon.id
                messages.success(request, "Coupon applied successfully!")

            else:
                messages.error(request, "Coupon expired or not valid.")

        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")

    return redirect("orders:checkout")

def remove_coupon(request):

    if "coupon_id" in request.session:
        del request.session["coupon_id"]

    messages.success(request, "Coupon removed.")

    return redirect("orders:checkout")

@login_required
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)

    status_map = {
        "ordered": 1,
        "packed": 2,
        "shipped": 3,
        "out_for_delivery": 4,
        "delivered": 5
    }
    items = OrderItem.objects.filter(order=order)
    current_step = status_map.get(order.status.lower(), 1)

    return render(request, "orders/order_detail.html", {
        "order": order,
        "current_step": current_step
    })

@login_required
def payment_page(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    upi_id = "risalrichu01@oksbi"
    store_name = "HOODLAB"

    upi_link = f"upi://pay?pa={upi_id}&pn={store_name}&am={order.total_amount}&cu=INR&tn=Order{order.id}"

    qr = qrcode.make(upi_link)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "orders/payment.html", {
        "order": order,
        "upi_link": upi_link,
        "qr_code": qr_base64
    })
@login_required
def confirm_payment(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.payment_status == "Pending":
        order.payment_status = "Submitted"
        order.save()

    messages.success(request, "Payment submitted for verification.")

    return redirect("orders:order_success")