from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name']
        labels = {
            'category_name': 'Category Name',
        }
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
        }

