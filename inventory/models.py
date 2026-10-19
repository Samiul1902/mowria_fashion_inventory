from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class UserProfile(models.Model):
    ROLE_SUPER_ADMIN = 'SUPER_ADMIN'
    ROLE_EMPLOYEE = 'EMPLOYEE'
    ROLE_VIEWER = 'VIEWER'

    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, 'Super Admin (Full Access)'),
        (ROLE_EMPLOYEE, 'Employee (Edit Stock Only)'),
        (ROLE_VIEWER, 'Viewer (Read Only)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_VIEWER)
    phone = models.CharField(max_length=25, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def can_manage_products(self):
        # Super admin can create, edit product details, delete product
        return self.user.is_superuser or self.role == self.ROLE_SUPER_ADMIN

    @property
    def can_adjust_stock(self):
        # Super admin and Employee can adjust stock (+ / -)
        return self.user.is_superuser or self.role in [self.ROLE_SUPER_ADMIN, self.ROLE_EMPLOYEE]

    @property
    def is_viewer(self):
        return not self.user.is_superuser and self.role == self.ROLE_VIEWER


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
    fabric_type = models.CharField(max_length=100, blank=True, null=True)
    gsm = models.CharField(max_length=30, blank=True, null=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    photo = models.ImageField(upload_to='products/%Y/%m/', blank=True, null=True)
    size_s = models.PositiveIntegerField(default=0)
    size_m = models.PositiveIntegerField(default=0)
    size_l = models.PositiveIntegerField(default=0)
    size_xl = models.PositiveIntegerField(default=0)
    size_xxl = models.PositiveIntegerField(default=0)

    # Garment Size Chart Specifications (in inches)
    # S: Chest, Length, Sleeves (s_shoulder field stores Sleeves)
    s_chest = models.DecimalField(max_digits=5, decimal_places=1, default=None, blank=True, null=True)
    s_length = models.DecimalField(max_digits=5, decimal_places=1, default=None, blank=True, null=True)
    s_shoulder = models.DecimalField(max_digits=5, decimal_places=1, default=None, blank=True, null=True)
    # M
    m_chest = models.DecimalField(max_digits=5, decimal_places=1, default=None, blank=True, null=True)
    m_length = models.DecimalField(max_digits=5, decimal_places=1, default=None, blank=True, null=True)
    m_shoulder = models.DecimalField(max_digits=5, decimal_places=1, default=None, blank=True, null=True)
    # L
    l_chest = models.DecimalField(max_digits=5, decimal_places=1, default=None, blank=True, null=True)
    l_length = models.DecimalField(max_digits=5, decimal_places=1, default=None, blank=True, null=True)
    l_shoulder = models.DecimalField(max_digits=5, decimal_places=1, default=None, blank=True, null=True)
    # XL
    xl_chest = models.DecimalField(max_digits=5, decimal_places=1, default=None, blank=True, null=True)
    xl_length = models.DecimalField(max_digits=5, decimal_places=1, default=None, blank=True, null=True)
    xl_shoulder = models.DecimalField(max_digits=5, decimal_places=1, default=None, blank=True, null=True)
    # XXL
    xxl_chest = models.DecimalField(max_digits=5, decimal_places=1, default=None, blank=True, null=True)
    xxl_length = models.DecimalField(max_digits=5, decimal_places=1, default=None, blank=True, null=True)
    xxl_shoulder = models.DecimalField(max_digits=5, decimal_places=1, default=None, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @classmethod
    def generate_sku(cls, category='T-Shirt', colour=''):
        """
        Auto-generates an apparel SKU following Option B:
        Format: MFB-<CATEGORY_CODE>-<COLOUR_CODE>-<COUNTER>
        e.g. MFB-TSH-NVY-001, MFB-POL-WHT-002
        """
        cat_map = {
            'T-Shirt': 'TSH',
            'Shirt': 'SHT',
            'Polo': 'POL',
            'Full Sleeve Shirt (Cotton)': 'FSC',
            'Full Sleeve (Cotton & wool)': 'FSW',
            'Other': 'OTH',
        }
        cat_code = cat_map.get(category, 'GEN')

        # Clean and extract 3-letter colour code
        clean_colour = (colour or '').strip().upper()
        colour_words = clean_colour.split()
        if len(colour_words) >= 2:
            colour_code = (colour_words[0][:2] + colour_words[1][:1])[:3]
        elif len(clean_colour) >= 3:
            colour_code = clean_colour[:3]
        elif len(clean_colour) > 0:
            colour_code = clean_colour.ljust(3, 'X')
        else:
            colour_code = 'GEN'

        prefix = f"MFB-{cat_code}-{colour_code}"

        # Find existing SKUs with this prefix to get the next sequential number
        similar = cls.objects.filter(code__startswith=prefix).values_list('code', flat=True)
        max_num = 0
        for code_str in similar:
            parts = code_str.split('-')
            if len(parts) >= 4 and parts[-1].isdigit():
                max_num = max(max_num, int(parts[-1]))

        next_num = max_num + 1
        return f"{prefix}-{next_num:03d}"

    def save(self, *args, **kwargs):
        if not self.code or not self.code.strip():
            self.code = self.generate_sku(self.category, self.colour)
        else:
            self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

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


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('PRODUCT_CREATED', 'Product Created'),
        ('PRODUCT_UPDATED', 'Product Updated'),
        ('PRODUCT_DELETED', 'Product Deleted'),
        ('STOCK_RESTOCKED', 'Stock Restocked'),
        ('STOCK_SOLD', 'Stock Sold'),
        ('USER_LOGIN', 'User Login'),
        ('USER_LOGOUT', 'User Logout'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    user_role = models.CharField(max_length=30, blank=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    product_code = models.CharField(max_length=30, blank=True)
    product_name = models.CharField(max_length=150, blank=True)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.user} - {self.action}: {self.details}"
