from django.contrib import admin
from .models import *

# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('label', 'email', 'created_at', 'session_id', 'total')
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)