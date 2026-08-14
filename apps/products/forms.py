from django import forms
from apps.products.models import Product, Category, ProductSize, ProductImage, SiteBanner

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-file'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'})
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['sku', 'product_id', 'name', 'category', 'description', 'price', 'discount_price', 'is_featured', 'is_new_arrival', 'is_active']
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'VAL-TSH-001'}),
            'product_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'PRD-1001'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Noir Heavyweight Hoodie'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_new_arrival': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class SiteBannerForm(forms.ModelForm):
    class Meta:
        model = SiteBanner
        fields = ['banner_type', 'title', 'subtitle', 'image']
        widgets = {
            'banner_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Optional Title'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Optional Subtitle'}),
            'image': forms.FileInput(attrs={'class': 'form-file'}),
        }

