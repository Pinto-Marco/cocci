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
    list_display = ('code', 'title', 'price', 'is_available', 'admin_barcode_actions')
    actions = ['print_selected_barcodes']
    exclude = ('barcode',)

    def admin_barcode_actions(self, obj):
        import urllib.parse
        download_url = f"/products/barcode/{obj.code}/"
        print_url = f"/products/print/?code={obj.code}&print=true"
        return format_html(
            '<a class="button" href="{}" download="{}_barcode.png" style="margin-right: 5px;">Download</a>'
            '<a class="button" href="{}" target="_blank">Print</a>',
            download_url,
            obj.code,
            print_url
        )

    admin_barcode_actions.short_description = 'Barcode Actions'

    def print_selected_barcodes(self, request, queryset):
        from django.http import HttpResponseRedirect
        # We will build the URL for the print page with the selected product IDs
        ids = ",".join([str(obj.id) for obj in queryset])
        url = f"/products/print/?ids={ids}&print=true"
        return HttpResponseRedirect(url)

    print_selected_barcodes.short_description = 'Print Selected Barcodes'

admin.site.register(product_models.Product, ProductAdmin)
admin.site.register(product_models.ProductHistory)
admin.site.register(product_models.Tag)
admin.site.register(product_models.ProductTag)

