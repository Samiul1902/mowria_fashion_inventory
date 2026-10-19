from django.contrib import admin
from .models import Product, StockMovement, UserProfile, ActivityLog

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'can_manage_products', 'can_adjust_stock')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'user_role', 'action', 'product_code', 'details')
    list_filter = ('action', 'user_role', 'timestamp')
    search_fields = ('user__username', 'product_code', 'product_name', 'details')
    readonly_fields = ('timestamp',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'colour', 'unit_cost', 'price', 'total_quantity', 'stock_status')
    list_filter = ('category', 'created_at')
    search_fields = ('code', 'name', 'colour')

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'size', 'quantity', 'unit_price', 'total_amount', 'timestamp')
    list_filter = ('movement_type', 'size', 'timestamp')
    search_fields = ('product__code', 'product__name', 'notes')
