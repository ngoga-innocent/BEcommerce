from django.contrib import admin
from .models import Product,ProductCategory,ProductImages


class ProductImageInline(admin.TabularInline):
    model=ProductImages
    extra=0
    fields=('image',)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines=[ProductImageInline]
    list_display = ('title','price','active','created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title','description')
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name','slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)