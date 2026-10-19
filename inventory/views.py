import json
import csv
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Sum, Q, Count
from .models import Product, StockMovement, UserProfile, ActivityLog
from .forms import ProductForm

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def get_user_role_context(request):
    if not request.user.is_authenticated:
        return {
            'role': 'VIEWER',
            'role_label': 'Viewer (Guest)',
            'can_manage_products': False,
            'can_adjust_stock': False,
            'is_super_admin': False,
            'is_employee': False,
            'is_viewer': True,
        }

    user = request.user
    if user.is_superuser:
        return {
            'role': 'SUPER_ADMIN',
            'role_label': 'Super Admin',
            'can_manage_products': True,
            'can_adjust_stock': True,
            'is_super_admin': True,
            'is_employee': False,
            'is_viewer': False,
        }

    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': UserProfile.ROLE_VIEWER})
    role = profile.role

    is_super_admin = (role == UserProfile.ROLE_SUPER_ADMIN)
    is_employee = (role == UserProfile.ROLE_EMPLOYEE)
    is_viewer = (role == UserProfile.ROLE_VIEWER)

    return {
        'role': role,
        'role_label': profile.get_role_display(),
        'can_manage_products': is_super_admin,
        'can_adjust_stock': is_super_admin or is_employee,
        'is_super_admin': is_super_admin,
        'is_employee': is_employee,
        'is_viewer': is_viewer,
    }

def log_activity(request, action, product=None, details=''):
    user = request.user if request.user.is_authenticated else None
    role_ctx = get_user_role_context(request)
    role_name = role_ctx['role_label']
    
    code = product.code if product else ''
    name = product.name if product else ''

    ActivityLog.objects.create(
        user=user,
        user_role=role_name,
        action=action,
        product_code=code,
        product_name=name,
        details=details,
        ip_address=get_client_ip(request)
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None
    if request.method == 'POST':
        identifier = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # Check by email or username
        username = identifier
        if '@' in identifier:
            matched_user = User.objects.filter(email__iexact=identifier).first()
            if matched_user:
                username = matched_user.username

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            log_activity(request, 'USER_LOGIN', details=f"User {user.email or user.username} logged in successfully.")
            return redirect('dashboard')
        else:
            error = "Invalid credentials. Please verify your email and password."

    return render(request, 'inventory/login.html', {'error': error})


def logout_view(request):
    if request.user.is_authenticated:
        log_activity(request, 'USER_LOGOUT', details=f"User {request.user.email or request.user.username} logged out.")
        logout(request)
    return redirect('login_view')


def dashboard(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    status = request.GET.get('status', '').strip()
    sort = request.GET.get('sort', 'newest').strip()

    products_qs = Product.objects.all().prefetch_related('movements')

    if query:
        products_qs = products_qs.filter(
            Q(code__iexact=query) |
            Q(code__icontains=query) |
            Q(name__icontains=query) |
            Q(category__icontains=query) |
            Q(colour__icontains=query)
        )

    if category:
        products_qs = products_qs.filter(category=category)

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
    else:
        product_list.sort(key=lambda p: p.created_at, reverse=True)

    # High-level KPIs & Analytics
    all_products = list(Product.objects.all().prefetch_related('movements'))
    total_active_skus = len(all_products)
    total_in_stock_units = sum(p.total_quantity for p in all_products)
    total_stock_value = sum(p.stock_value for p in all_products)
    total_potential_revenue = sum(p.potential_revenue for p in all_products)
    total_expected_profit = sum(p.expected_profit for p in all_products)
    low_stock_count = sum(1 for p in all_products if p.stock_status == 'Low Stock')
    out_of_stock_count = sum(1 for p in all_products if p.stock_status == 'Out of Stock')

    total_units_sold = StockMovement.objects.filter(movement_type='SALE').aggregate(
        total=Sum('quantity')
    )['total'] or 0

    # Analytics: Overall Margin & Capital ROI
    overall_avg_margin = (
        round(((total_potential_revenue - total_stock_value) / total_potential_revenue) * 100, 1)
        if total_potential_revenue > Decimal('0.00') else 0.0
    )
    projected_roi = (
        round((total_expected_profit / total_stock_value) * 100, 1)
        if total_stock_value > Decimal('0.00') else 0.0
    )

    # Analytics: Size Distribution Totals Across Entire Inventory
    total_s = sum(p.size_s for p in all_products)
    total_m = sum(p.size_m for p in all_products)
    total_l = sum(p.size_l for p in all_products)
    total_xl = sum(p.size_xl for p in all_products)
    total_xxl = sum(p.size_xxl for p in all_products)

    size_distribution_chart = {
        's': total_s,
        'm': total_m,
        'l': total_l,
        'xl': total_xl,
        'xxl': total_xxl,
    }

    # Analytics: Category Valuation Breakdown
    category_choices = [c[0] for c in Product.CATEGORY_CHOICES]
    category_counts = []
    category_analytics = []

    for cat in category_choices:
        cat_prods = [p for p in all_products if p.category == cat]
        cat_count = len(cat_prods)
        cat_stock = sum(p.total_quantity for p in cat_prods)
        cat_val = sum(p.stock_value for p in cat_prods)

        category_counts.append({
            'name': cat,
            'count': cat_count
        })
        if cat_stock > 0 or cat_count > 0:
            category_analytics.append({
                'name': cat,
                'count': cat_count,
                'stock': cat_stock,
                'valuation': float(cat_val),
            })

    product_form = ProductForm()
    user_perm = get_user_role_context(request)
    recent_activities = ActivityLog.objects.all()[:10]

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
            'overall_avg_margin': overall_avg_margin,
            'projected_roi': projected_roi,
        },
        'size_distribution': size_distribution_chart,
        'category_analytics': category_analytics,
        'categories': category_counts,
        'selected_category': category,
        'selected_status': status,
        'selected_sort': sort,
        'query': query,
        'product_form': product_form,
        'user_perm': user_perm,
        'recent_activities': recent_activities,
    }
    return render(request, 'inventory/dashboard.html', context)


@require_POST
def product_create(request):
    user_perm = get_user_role_context(request)
    if not user_perm['can_manage_products']:
        return HttpResponseForbidden("Access Denied: Only Super Admin can create new apparel products.")

    form = ProductForm(request.POST, request.FILES)
    if form.is_valid():
        product = form.save()
        log_activity(
            request, 
            'PRODUCT_CREATED', 
            product=product, 
            details=f"Created SKU {product.code} - {product.name} with initial stock of {product.total_quantity} units (Wholesale: ৳{product.unit_cost}, Retail: ৳{product.price})"
        )
    return redirect('dashboard')


@require_POST
def product_update(request, pk):
    user_perm = get_user_role_context(request)
    if not user_perm['can_manage_products']:
        return HttpResponseForbidden("Access Denied: Only Super Admin can modify product details.")

    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST, request.FILES, instance=product)
    if form.is_valid():
        product = form.save()
        log_activity(
            request, 
            'PRODUCT_UPDATED', 
            product=product, 
            details=f"Updated product specs: '{product.name}' (Category: {product.category}, Retail: ৳{product.price}, Cost: ৳{product.unit_cost})"
        )
    return redirect('dashboard')


@require_POST
def product_delete(request, pk):
    user_perm = get_user_role_context(request)
    if not user_perm['can_manage_products']:
        return HttpResponseForbidden("Access Denied: Only Super Admin can delete products.")

    product = get_object_or_404(Product, pk=pk)
    code = product.code
    name = product.name
    if product.photo:
        try:
            product.photo.delete(save=False)
        except Exception:
            pass
    product.delete()
    log_activity(
        request, 
        'PRODUCT_DELETED', 
        details=f"Permanently deleted SKU {code} - {name}"
    )
    return redirect('dashboard')


@require_POST
def adjust_size_stock(request, pk):
    user_perm = get_user_role_context(request)
    if not user_perm['can_adjust_stock']:
        return JsonResponse({
            'success': False, 
            'error': 'Access Denied: Viewer accounts cannot edit stock. Please switch to Employee or Super Admin.'
        }, status=403)

    product = get_object_or_404(Product, pk=pk)
    
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

    setattr(product, field_name, new_val)
    product.save(update_fields=[field_name, 'updated_at'])

    if delta > 0:
        StockMovement.objects.create(
            product=product,
            movement_type='RESTOCK',
            size=size.upper(),
            quantity=abs(delta),
            unit_price=product.unit_cost,
            notes='Quick adjustment (+1 Restock)'
        )
        log_activity(
            request, 
            'STOCK_RESTOCKED', 
            product=product, 
            details=f"Restocked +{delta} unit(s) of size {size.upper()}. New size stock: {new_val}"
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
        log_activity(
            request, 
            'STOCK_SOLD', 
            product=product, 
            details=f"Recorded sale of {abs(delta)} unit(s) of size {size.upper()} at ৳{product.price}. Remaining: {new_val}"
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


def export_inventory_csv(request):
    """Excel / CSV Export replacing manual sheets"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Mowria_Fashion_Inventory.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'SKU Code', 'Name', 'Category', 'Colour',
        'Unit Cost (BDT)', 'Retail Price (BDT)',
        'Size S', 'Size M', 'Size L', 'Size XL', 'Size 2XL',
        'Total Quantity', 'Stock Valuation (BDT)', 'Potential Revenue (BDT)',
        'Expected Profit (BDT)', 'Margin %', 'Units Sold', 'Stock Status'
    ])

    for p in Product.objects.all():
        writer.writerow([
            p.code, p.name, p.category, p.colour or '',
            p.unit_cost, p.price,
            p.size_s, p.size_m, p.size_l, p.size_xl, p.size_xxl,
            p.total_quantity, p.stock_value, p.potential_revenue,
            p.expected_profit, round(p.profit_margin, 1), p.sold_quantity, p.stock_status
        ])

    return response


def activity_log_view(request):
    logs = ActivityLog.objects.all()[:150]
    user_perm = get_user_role_context(request)
    return render(request, 'inventory/activity_log.html', {
        'logs': logs,
        'user_perm': user_perm
    })


def quick_switch_demo_role(request):
    target_role = request.GET.get('role', 'SUPER_ADMIN').upper()
    role_map = {
        'SUPER_ADMIN': ('superadmin@mowriafashion.com', UserProfile.ROLE_SUPER_ADMIN, True),
        'EMPLOYEE': ('salesrep@mowriafashion.com', UserProfile.ROLE_EMPLOYEE, False),
        'VIEWER': ('view@mowriafashion.com', UserProfile.ROLE_VIEWER, False),
    }

    if target_role not in role_map:
        return redirect('dashboard')

    email, role_const, is_super = role_map[target_role]
    username = email.split('@')[0]
    user, _ = User.objects.get_or_create(username=username, defaults={'email': email})
    user.email = email
    user.is_superuser = is_super
    user.is_staff = is_super
    user.save()

    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.role = role_const
    profile.save()

    login(request, user)
    log_activity(request, 'USER_LOGIN', details=f"Switched session role to {profile.get_role_display()}")
    return redirect('dashboard')
