from django.contrib import admin

from house.models import Category, Product, Order, OrderItem, ProductTransfer


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse')
    list_filter = ('warehouse',)
    search_fields = ('name',)

    def warehouse(self, obj):
        return obj.warehouse

    warehouse.short_description = 'Warehouse'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'sku', 'unit', 'price', 'base_price', 'discount_price',
        'quantity', 'min_quantity', 'format_category', 'format_warehouse'
    )
    search_fields = ('name', 'sku',)
    list_filter = ('warehouse',)

    def format_warehouse(self, obj):
        return obj.warehouse.name if obj.warehouse else '-'

    format_warehouse.short_description = 'Warehouse'

    def format_category(self, obj):
        return obj.categories.name if obj.categories else '-'

    format_category.short_description = 'Category'


# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = (
#         'product_name', 'price', 'quantity', 'product_unit'
#     )
#     search_fields = ('product_name',)
#     # list_filter = ('order__warehouse')
#
#     def product_name(self, obj):
#         return obj.product.name
#
#     product_name.short_description = 'Product'
#
#     def price(self, obj):
#         if obj.discount_price and obj.discount_price > 0:
#             return obj.discount_price
#         return obj.base_price
#
#     def product_unit(self, obj):
#         return obj.product.unit
#
#     product_unit.short_description = 'Unit'
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    inlines = [OrderItemInline]

    def save_formset(self, request, form, formset, change):
        # Avval saqlab olamiz
        instances = formset.save(commit=False)
        for obj in instances:
            product = obj.product
            if product and obj.quantity:
                # Quantity yetarliligini tekshirish mumkin
                if product.quantity < obj.quantity:
                    raise ValueError(
                        f"{product.name} mahsulotida yetarli quantity mavjud emas!"
                    )
                # Mahsulot quantity’sini kamaytirish
                product.quantity -= obj.quantity
                product.save(update_fields=['quantity'])
            obj.save()
        formset.save_m2m()


@admin.register(ProductTransfer)
class ProductTransferAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'from_warehouse', 'to_warehouse', 'transferred_at')
    list_filter = ('from_warehouse', 'to_warehouse', 'product', 'transferred_at')
    search_fields = ('product__name',)
