from django import forms
from .models import Account, UserProfile
from Category.models import Category
from Store.models import Product, Variation, VariationType


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
    }))
    is_manager = forms.BooleanField(required=False, label="Registrati come manager")

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password', 'is_manager']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={'invalid': "Image files only"}, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name']  # Rimuovo lo slug dal form
        labels = {
            'category_name': 'Category Name',
        }
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
        }

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

class StockUpdateForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), label="Product", widget=forms.Select(attrs={'class': 'form-control'}))
    quantity = forms.IntegerField(label="New quantity", min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}))

class AddVariationTypesForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), label="Product", widget=forms.Select(attrs={'class': 'form-control'}))
    variation_type_names = forms.CharField(
        label="Variation types (one per line)",
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Example: color\nsize'}),
        help_text="Enter one or more variation types (e.g. color, size, material), one per line. They will be created together with the product."
    )

class RemoveVariationTypeForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), label="Product", widget=forms.Select(attrs={'class': 'form-control'}))
    variation_type = forms.ModelChoiceField(queryset=VariationType.objects.none(), label="Variation type", widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        product_id = kwargs.pop('product_id', None)
        super().__init__(*args, **kwargs)
        if product_id:
            self.fields['variation_type'].queryset = VariationType.objects.filter(product_id=product_id)
        else:
            self.fields['variation_type'].queryset = VariationType.objects.none()
