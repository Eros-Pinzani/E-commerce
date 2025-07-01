from django import forms
from .models import VariationType, Variation, Product


class VariationTypeForm(forms.ModelForm):
    variation_values = forms.CharField(
        required=True,
        widget=forms.HiddenInput(),
        help_text="Inserisci almeno un valore per la variazione."
    )

    class Meta:
        model = VariationType
        fields = ['product', 'name', 'variation_values']

    def clean_variation_values(self):
        data = self.cleaned_data['variation_values']
        # Controllo esplicito per stringa vuota o solo spazi
        if not data or not data.strip():
            raise forms.ValidationError('Devi inserire almeno un valore per la variazione.')
        values = [v.strip() for v in data.split(',') if v.strip()]
        if not values:
            raise forms.ValidationError('Devi inserire almeno un valore per la variazione.')
        return data

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'description', 'price', 'images', 'stock', 'category']
        labels = {
            'product_name': 'Product Name',
            'description': 'Description',
            'price': 'Price',
            'images': 'Images',
            'stock': 'Stock',
            'category': 'Category',
        }
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'}),
            'images': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

class VariationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        product_id = kwargs.pop('product_id', None)
        super().__init__(*args, **kwargs)
        if product_id:
            self.fields['variation_category'].queryset = VariationType.objects.filter(product_id=product_id)
        else:
            self.fields['variation_category'].queryset = VariationType.objects.none()
    class Meta:
        model = Variation
        fields = ['product', 'variation_category', 'variation_value', 'is_active']
        labels = {
            'product': 'Product',
            'variation_category': 'Variation Type',
            'variation_value': 'Value',
            'is_active': 'Active',
        }
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'variation_category': forms.Select(attrs={'class': 'form-control'}),
            'variation_value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Value'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
