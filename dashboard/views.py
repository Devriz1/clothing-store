from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.contrib.auth import get_user_model
from orders.models import Order
from store.models import Product
import json
from .forms import AdminProductForm

User = get_user_model()


@staff_member_required
def admin_dashboard(request):

    # Update order status
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        status = request.POST.get("status")
        payment_status = request.POST.get("payment_status")

        order = Order.objects.get(id=order_id)
        order.status = status
        order.payment_status = payment_status
        order.save()

        return redirect('dashboard:admin_dashboard')

    total_orders = Order.objects.count()
    total_users = User.objects.count()
    total_products = Product.objects.count()

    total_revenue = Order.objects.aggregate(
        Sum('total_amount')
    )['total_amount__sum'] or 0

    low_stock_products = Product.objects.filter(stock__lt=5)

    recent_orders = Order.objects.all().order_by('-created_at')

    # ✅ Monthly Revenue Data
    monthly_data = (
        Order.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )

    months = []
    revenues = []

    for data in monthly_data:
        if data['month']:  # avoid None errors
            months.append(data['month'].strftime('%B'))
            revenues.append(float(data['total']))

    context = {
        'total_orders': total_orders,
        'total_users': total_users,
        'total_products': total_products,
        'total_revenue': total_revenue,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
        'months': json.dumps(months),
        'revenues': json.dumps(revenues),
    }

    return render(request, 'dashboard/dashboard.html', context)

@staff_member_required
def add_product(request):
    if request.method == "POST":
        form = AdminProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard:admin_dashboard')
    else:
        form = AdminProductForm()

    return render(request, 'dashboard/add_product.html', {'form': form})