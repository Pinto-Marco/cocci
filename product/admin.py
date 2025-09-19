from django.contrib import admin
from django.utils.html import format_html
from . import models as product_models
from django.conf import settings
import os

class ProductImageInline(admin.TabularInline):  # Inline per le immagini del prodotto
    model = product_models.ProductImage
    extra = 0
    fields = ('image_tag', 'image',)  # Mostra sia preview che campo editabile
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        if obj.image:
            if obj.image.startswith("http"):
                url = obj.image
            else:
                from django.conf import settings
                import os
                url = os.path.join(settings.MEDIA_URL, obj.image)
            return format_html('<img src="{}" width="80" height="80" />', url)
        return "-"
    image_tag.short_description = "Preview"

class ProductTagInline(admin.TabularInline):  # Inline per i tag del prodotto
    model = product_models.ProductTag
    extra = 0

# ProductCategoryInline
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductTagInline]
    list_display = ('first_image', 'code', 'title', 'price', 'is_available') 
    # list_filter = ('price', 'tags__tag__name', 'is_available', 'title')
    list_filter = ('price', 'is_available', 'title', 'producttag__tag__name')
    # filtro per: prezzo, tag, is_available, title, 

    def barcode_image(self, obj):
        if obj.barcode:
            return format_html('<img src="{}" width="100" height="100" />', obj.barcode.url)
        return "No barcode"

    barcode_image.short_description = 'Barcode'

    def first_image(self, obj):
        image_obj = obj.productimage_set.first()
        if image_obj and image_obj.image:
            image_path = image_obj.image
            # Mostra direttamente se è un URL assoluto
            if image_path.startswith("http"):
                image_url = image_path
            else:
                from django.conf import settings
                import os
                image_url = os.path.join(settings.MEDIA_URL, image_path)
            return format_html('<img src="{}" width="60" height="60" />', image_url)
        return "-"
    first_image.short_description = "Image"
    
    # def first_image(self, obj):
    #     image_obj = obj.productimage_set.first()
    #     if image_obj and image_obj.image:
    #         # Se fosse un ImageField: usa <img src="...">
    #         # return format_html('<img src="{}" width="60" height="60" />', image_obj.image.url)
    #         return image_obj.image  # Attualmente solo path/testo perché è un CharField
    #     return "-"

    # first_image.short_description = "Image"

admin.site.register(product_models.Product, ProductAdmin)
admin.site.register(product_models.ProductHistory)
admin.site.register(product_models.Tag)
admin.site.register(product_models.ProductTag)

