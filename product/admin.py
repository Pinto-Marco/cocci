from django.contrib import admin
from django.utils.html import format_html
from . import models as product_models

class ProductImageInline(admin.TabularInline):  # Inline per le immagini del prodotto
    model = product_models.ProductImage
    extra = 1

class ProductCategoryInline(admin.TabularInline):  # Inline per le categorie del prodotto
    model = product_models.ProductCategory
    extra = 1

class ProductTagInline(admin.TabularInline):  # Inline per i tag del prodotto
    model = product_models.ProductTag
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductCategoryInline, ProductTagInline]  # Aggiungi gli inline alla vista
    list_display = ('code', 'title', 'price', 'barcode_image')  # Aggiungi barcode_image alla lista

    def barcode_image(self, obj):
        if obj.barcode:
            return format_html('<img src="{}" width="100" height="100" />', obj.barcode.url)
        return "No barcode"

    barcode_image.short_description = 'Barcode'  # Nome del campo nell'admin

admin.site.register(product_models.Product, ProductAdmin)
admin.site.register(product_models.ProductHistory)
admin.site.register(product_models.ProductCategory)
admin.site.register(product_models.Category)
admin.site.register(product_models.Tag)
admin.site.register(product_models.ProductTag)

