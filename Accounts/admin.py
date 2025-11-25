from django.contrib import admin
from .models import CustomUser
# Register your models here.
@admin.register(CustomUser)
class User(admin.ModelAdmin):
    list_display = ('username','phone_number','allowed_to_post','is_active')
    
    search_fields = ('phone_number',)