from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from store.models import ProductVariant
from .models import CartItem
from .models import Cart
from django.shortcuts import render

@login_required
def add_to_cart(request):

    if request.method == "POST":

        variant_id = request.POST.get("variant_id")

        variant = get_object_or_404(ProductVariant, id=variant_id)

        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if item already exists
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

    return redirect("cart:cart_detail")

@login_required
def update_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    action = request.GET.get('action')

    if action == 'increase':
        if item.quantity < item.variant.stock:
            item.quantity += 1
            item.save()

    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()

    return redirect('cart:cart_detail')

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart:cart_detail')

@login_required
def update_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    action = request.GET.get('action')

    if action == 'increase':
        if item.quantity < item.variant.stock:
            item.quantity += 1
            item.save()

    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()

    return redirect('cart:cart_detail')