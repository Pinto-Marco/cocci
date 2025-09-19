from django.contrib import admin
from django.utils.html import format_html
from . import models as product_models

class ProductImageInline(admin.TabularInline):  # Inline per le immagini del prodotto
    model = product_models.ProductImage
    extra = 0

class ProductTagInline(admin.TabularInline):  # Inline per i tag del prodotto
    model = product_models.ProductTag
    extra = 0

# ProductCategoryInline
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductTagInline]
    list_display = ('code', 'title', 'price', 'is_available', 'first_image') 

    def barcode_image(self, obj):
        if obj.barcode:
            return format_html('<img src="{}" width="100" height="100" />', obj.barcode.url)
        return "No barcode"

    barcode_image.short_description = 'Barcode'

    def first_image(self, obj):
        image_obj = obj.productimage_set.first()
        if image_obj and image_obj.image:
            # Se fosse un ImageField: usa <img src="...">
            # return format_html('<img src="{}" width="60" height="60" />', image_obj.image.url)
            return image_obj.image  # Attualmente solo path/testo perché è un CharField
        return "-"

    first_image.short_description = "Image"

admin.site.register(product_models.Product, ProductAdmin)
admin.site.register(product_models.ProductHistory)
admin.site.register(product_models.Tag)
admin.site.register(product_models.ProductTag)

