from django.contrib import admin
from .models import Product, StockMovement

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
