from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'code', 'name', 'category', 'colour',
            'unit_cost', 'price', 'photo',
            'size_s', 'size_m', 'size_l', 'size_xl', 'size_xxl'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-mono text-sm uppercase',
                'placeholder': 'e.g. MFB-0001',
                'required': True
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm',
                'placeholder': 'e.g. Lacoste Polo White',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm'
            }),
            'colour': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm',
                'placeholder': 'e.g. Navy Blue'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'w-full text-xs text-slate-400 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-emerald-600 file:text-white hover:file:bg-emerald-500 cursor-pointer',
                'accept': 'image/*'
            }),
            'size_s': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1.5 bg-slate-900 border border-slate-700 rounded text-center text-white text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'min': '0'
            }),
            'size_m': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1.5 bg-slate-900 border border-slate-700 rounded text-center text-white text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'min': '0'
            }),
            'size_l': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1.5 bg-slate-900 border border-slate-700 rounded text-center text-white text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'min': '0'
            }),
            'size_xl': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1.5 bg-slate-900 border border-slate-700 rounded text-center text-white text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'min': '0'
            }),
            'size_xxl': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1.5 bg-slate-900 border border-slate-700 rounded text-center text-white text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'min': '0'
            }),
        }

