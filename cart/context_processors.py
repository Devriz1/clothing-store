def cart_count(request):

    if request.user.is_authenticated:
        cart = getattr(request.user, "cart", None)

        if cart:
            count = sum(item.quantity for item in cart.items.all())
        else:
            count = 0
    else:
        count = 0

    return {"cart_count": count}