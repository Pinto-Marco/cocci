from django.contrib import admin
from django.utils.html import format_html
from . import models as product_models
from django.conf import settings
import os
from django_admin_multi_select_filter.filters import MultiSelectRelatedFieldListFilter
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter, NumericRangeFilter

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

class TagFilter(admin.SimpleListFilter):
    title = 'tag'
    parameter_name = 'tag'

    def lookups(self, request, model_admin):
        tags = set(product_models.Tag.objects.all().values_list('name', flat=True))
        return [(tag, tag) for tag in tags]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(producttag__tag__name__icontains=self.value())
        return queryset

# Per filtro range prezzo (min e max)
class PriceRangeFilter(admin.SimpleListFilter):
    title = 'price range'
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return (('custom', 'Custom price range'),)

    def queryset(self, request, queryset):
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        if min_price and max_price:
            try:
                min_price = float(min_price)
                max_price = float(max_price)
                return queryset.filter(price__gte=min_price, price__lte=max_price)
            except ValueError:
                pass
        return queryset


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

