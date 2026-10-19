from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('T-Shirt', 'T-Shirt'),
        ('Shirt', 'Shirt'),
        ('Polo', 'Polo'),
        ('Full Sleeve Shirt (Cotton)', 'Full Sleeve Shirt (Cotton)'),
        ('Full Sleeve (Cotton & wool)', 'Full Sleeve (Cotton & wool)'),
        ('Other', 'Other'),
    ]

    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=60, choices=CATEGORY_CHOICES, default='T-Shirt')
    colour = models.CharField(max_length=50, blank=True, null=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    photo = models.ImageField(upload_to='products/%Y/%m/', blank=True, null=True)
    size_s = models.PositiveIntegerField(default=0)
    size_m = models.PositiveIntegerField(default=0)
    size_l = models.PositiveIntegerField(default=0)
    size_xl = models.PositiveIntegerField(default=0)
    size_xxl = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def total_quantity(self):
        return self.size_s + self.size_m + self.size_l + self.size_xl + self.size_xxl

    @property
    def stock_value(self):
        return self.total_quantity * self.unit_cost

    @property
    def potential_revenue(self):
        return self.total_quantity * self.price

    @property
    def expected_profit(self):
        return self.potential_revenue - self.stock_value

    @property
    def profit_margin(self):
        if self.price > Decimal('0.00'):
            return float((self.price - self.unit_cost) / self.price) * 100.0
        return 0.0

    @property
    def stock_status(self):
        qty = self.total_quantity
        if qty == 0:
            return 'Out of Stock'
        elif qty <= 5:
            return 'Low Stock'
        return 'In Stock'

    @property
    def sold_quantity(self):
        # Dynamically compute total units sold from movements
        sales = self.movements.filter(movement_type='SALE').aggregate(total_sold=models.Sum('quantity'))['total_sold']
        return sales or 0


class StockMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ('SALE', 'Sale'),
        ('RESTOCK', 'Restock'),
        ('RETURN', 'Return'),
    ]

    SIZE_CHOICES = [
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPE_CHOICES)
    size = models.CharField(max_length=5, choices=SIZE_CHOICES)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def save(self, *args, **kwargs):
        if self.unit_price is not None and self.quantity is not None:
            self.total_amount = Decimal(self.quantity) * Decimal(self.unit_price)
        else:
            self.total_amount = Decimal('0.00')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.movement_type} {self.quantity}x {self.product.code} ({self.size})"
