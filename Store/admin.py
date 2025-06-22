from django.contrib import admin
from .models import Product, Variation, VariationType

# Register your models here.

class VariationTypeInline(admin.TabularInline):
    model = VariationType
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [VariationTypeInline]

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')
    fields = ('product', 'variation_category', 'variation_value', 'is_active')

admin.site.register(Product, ProductAdmin)
admin.site.register(VariationType)
admin.site.register(Variation, VariationAdmin)