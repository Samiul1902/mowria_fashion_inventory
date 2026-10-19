from django import forms
from .models import Product

input_base_cls = (
    "w-full px-3 py-2 rounded-xl text-sm font-medium transition duration-200 "
    "bg-white dark:bg-slate-900 "
    "border border-slate-300 dark:border-slate-700 "
    "text-slate-800 dark:text-slate-100 "
    "placeholder-slate-400 dark:placeholder-slate-500 "
    "focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500"
)

size_input_cls = (
    "w-full px-2 py-2 rounded-lg text-center text-sm font-bold transition duration-200 "
    "bg-white dark:bg-slate-900 "
    "border border-slate-300 dark:border-slate-700 "
    "text-slate-800 dark:text-slate-100 "
    "focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500"
)

chart_input_cls = (
    "w-full px-1.5 py-1 rounded text-center text-xs font-semibold "
    "bg-white dark:bg-slate-900 "
    "border border-slate-300 dark:border-slate-700 "
    "text-slate-800 dark:text-slate-100 "
    "focus:outline-none focus:ring-1 focus:ring-blue-500"
)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'code', 'name', 'category', 'colour',
            'unit_cost', 'price', 'photo',
            'size_s', 'size_m', 'size_l', 'size_xl', 'size_xxl',
            's_chest', 's_length', 's_shoulder',
            'm_chest', 'm_length', 'm_shoulder',
            'l_chest', 'l_length', 'l_shoulder',
            'xl_chest', 'xl_length', 'xl_shoulder',
            'xxl_chest', 'xxl_length', 'xxl_shoulder',
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': f"{input_base_cls} font-mono uppercase tracking-wider",
                'placeholder': 'e.g. MFB-0001',
                'required': True
            }),
            'name': forms.TextInput(attrs={
                'class': input_base_cls,
                'placeholder': 'e.g. Lacoste Polo White',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': input_base_cls
            }),
            'colour': forms.TextInput(attrs={
                'class': input_base_cls,
                'placeholder': 'e.g. Navy Blue'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': input_base_cls,
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'price': forms.NumberInput(attrs={
                'class': input_base_cls,
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'w-full text-xs text-slate-500 dark:text-slate-400 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 cursor-pointer transition',
                'accept': 'image/*'
            }),
            'size_s': forms.NumberInput(attrs={'class': size_input_cls, 'min': '0'}),
            'size_m': forms.NumberInput(attrs={'class': size_input_cls, 'min': '0'}),
            'size_l': forms.NumberInput(attrs={'class': size_input_cls, 'min': '0'}),
            'size_xl': forms.NumberInput(attrs={'class': size_input_cls, 'min': '0'}),
            'size_xxl': forms.NumberInput(attrs={'class': size_input_cls, 'min': '0'}),
            
            # Size Chart widgets
            's_chest': forms.NumberInput(attrs={'class': chart_input_cls, 'step': '0.5'}),
            's_length': forms.NumberInput(attrs={'class': chart_input_cls, 'step': '0.5'}),
            's_shoulder': forms.NumberInput(attrs={'class': chart_input_cls, 'step': '0.5'}),

            'm_chest': forms.NumberInput(attrs={'class': chart_input_cls, 'step': '0.5'}),
            'm_length': forms.NumberInput(attrs={'class': chart_input_cls, 'step': '0.5'}),
            'm_shoulder': forms.NumberInput(attrs={'class': chart_input_cls, 'step': '0.5'}),

            'l_chest': forms.NumberInput(attrs={'class': chart_input_cls, 'step': '0.5'}),
            'l_length': forms.NumberInput(attrs={'class': chart_input_cls, 'step': '0.5'}),
            'l_shoulder': forms.NumberInput(attrs={'class': chart_input_cls, 'step': '0.5'}),

            'xl_chest': forms.NumberInput(attrs={'class': chart_input_cls, 'step': '0.5'}),
            'xl_length': forms.NumberInput(attrs={'class': chart_input_cls, 'step': '0.5'}),
            'xl_shoulder': forms.NumberInput(attrs={'class': chart_input_cls, 'step': '0.5'}),

            'xxl_chest': forms.NumberInput(attrs={'class': chart_input_cls, 'step': '0.5'}),
            'xxl_length': forms.NumberInput(attrs={'class': chart_input_cls, 'step': '0.5'}),
            'xxl_shoulder': forms.NumberInput(attrs={'class': chart_input_cls, 'step': '0.5'}),
        }
