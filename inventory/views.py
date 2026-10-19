import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Q
from .models import Product, StockMovement
from .forms import ProductForm

def dashboard(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    status = request.GET.get('status', '').strip()
    sort = request.GET.get('sort', 'newest').strip()

    products_qs = Product.objects.all().prefetch_related('movements')

    # Filtering
    if query:
        products_qs = products_qs.filter(
            Q(code__icontains=query) |
            Q(name__icontains=query) |
            Q(category__icontains=query) |
            Q(colour__icontains=query)
        )

    if category:
        products_qs = products_qs.filter(category=category)

    # Convert to list to support property-based filtering/sorting & dynamic annotations
    product_list = list(products_qs)

    if status:
        if status == 'In Stock':
            product_list = [p for p in product_list if p.stock_status == 'In Stock']
        elif status == 'Low Stock':
            product_list = [p for p in product_list if p.stock_status == 'Low Stock']
        elif status == 'Out of Stock':
            product_list = [p for p in product_list if p.stock_status == 'Out of Stock']

    # Sorting
    if sort == 'price_asc':
        product_list.sort(key=lambda p: p.price)
    elif sort == 'price_desc':
        product_list.sort(key=lambda p: p.price, reverse=True)
    elif sort == 'quantity_asc':
        product_list.sort(key=lambda p: p.total_quantity)
    elif sort == 'quantity_desc':
        product_list.sort(key=lambda p: p.total_quantity, reverse=True)
    elif sort == 'sold_desc':
        product_list.sort(key=lambda p: p.sold_quantity, reverse=True)
    elif sort == 'name_asc':
        product_list.sort(key=lambda p: p.name.lower())
    else:  # default newest
        product_list.sort(key=lambda p: p.created_at, reverse=True)

    # High-level KPIs across all products in inventory
    all_products = Product.objects.all().prefetch_related('movements')
    total_active_skus = all_products.count()
    total_in_stock_units = sum(p.total_quantity for p in all_products)
    total_stock_value = sum(p.stock_value for p in all_products)
    total_potential_revenue = sum(p.potential_revenue for p in all_products)
    total_expected_profit = sum(p.expected_profit for p in all_products)
    low_stock_count = sum(1 for p in all_products if p.stock_status == 'Low Stock')
    out_of_stock_count = sum(1 for p in all_products if p.stock_status == 'Out of Stock')

    # Total units sold across all products
    total_units_sold = StockMovement.objects.filter(movement_type='SALE').aggregate(
        total=Sum('quantity')
    )['total'] or 0

    # Category counts for filter pills
    category_choices = [c[0] for c in Product.CATEGORY_CHOICES]
    category_counts = []
    for cat in category_choices:
        count = Product.objects.filter(category=cat).count()
        category_counts.append({
            'name': cat,
            'count': count
        })

    product_form = ProductForm()

    context = {
        'products': product_list,
        'kpis': {
            'total_active_skus': total_active_skus,
            'total_in_stock_units': total_in_stock_units,
            'total_units_sold': total_units_sold,
            'total_stock_value': total_stock_value,
            'total_potential_revenue': total_potential_revenue,
            'total_expected_profit': total_expected_profit,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
        },
        'categories': category_counts,
        'selected_category': category,
        'selected_status': status,
        'selected_sort': sort,
        'query': query,
        'product_form': product_form,
    }
    return render(request, 'inventory/dashboard.html', context)


@require_POST
def product_create(request):
    form = ProductForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
    return redirect('dashboard')


@require_POST
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST, request.FILES, instance=product)
    if form.is_valid():
        form.save()
    return redirect('dashboard')


@require_POST
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # If photo exists locally, could optionally clean up or let storage handle
    if product.photo:
        try:
            product.photo.delete(save=False)
        except Exception:
            pass
    product.delete()
    return redirect('dashboard')


@require_POST
def adjust_size_stock(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Check if JSON payload or Form data
    size = None
    delta = 0
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            size = data.get('size', '').lower()
            delta = int(data.get('delta', 0))
        except (ValueError, TypeError):
            return HttpResponseBadRequest("Invalid JSON")
    else:
        size = request.POST.get('size', '').lower()
        try:
            delta = int(request.POST.get('delta', 0))
        except (ValueError, TypeError):
            return HttpResponseBadRequest("Invalid delta")

    valid_sizes = {'s': 'size_s', 'm': 'size_m', 'l': 'size_l', 'xl': 'size_xl', 'xxl': 'size_xxl'}
    if size not in valid_sizes:
        return HttpResponseBadRequest(f"Invalid size '{size}'")

    field_name = valid_sizes[size]
    current_val = getattr(product, field_name)
    new_val = current_val + delta

    if new_val < 0:
        return JsonResponse({
            'success': False,
            'error': 'Stock count cannot be negative.'
        }, status=400)

    # Set new value
    setattr(product, field_name, new_val)
    product.save(update_fields=[field_name, 'updated_at'])

    # Record stock movement
    # If delta > 0: RESTOCK; if delta < 0: SALE
    if delta > 0:
        StockMovement.objects.create(
            product=product,
            movement_type='RESTOCK',
            size=size.upper(),
            quantity=abs(delta),
            unit_price=product.unit_cost,
            notes='Quick adjustment (+1 Restock)'
        )
    elif delta < 0:
        StockMovement.objects.create(
            product=product,
            movement_type='SALE',
            size=size.upper(),
            quantity=abs(delta),
            unit_price=product.price,
            notes='Quick adjustment (-1 Sale)'
        )

    return JsonResponse({
        'success': True,
        'product_id': product.pk,
        'size': size,
        'new_size_qty': new_val,
        'total_quantity': product.total_quantity,
        'stock_status': product.stock_status,
        'stock_value': float(product.stock_value),
        'potential_revenue': float(product.potential_revenue),
        'expected_profit': float(product.expected_profit),
        'sold_quantity': product.sold_quantity,
        'profit_margin': round(product.profit_margin, 1)
    })
