from django.contrib import admin

from .models import (
    Division,
    District,
    Representative,
    TeaProduct,
    TeaPackage,
    Sale,
    SaleItem,
)


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "division")
    list_filter = ("division",)
    search_fields = ("name",)


@admin.register(Representative)
class RepresentativeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "employee_id", "district", "active")
    list_filter = ("active", "district__division")
    search_fields = ("name", "employee_id")


@admin.register(TeaProduct)
class TeaProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(TeaPackage)
class TeaPackageAdmin(admin.ModelAdmin):
    list_display = ("product", "weight_grams", "price")
    list_filter = ("product",)


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ("unit_price", "total")


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "representative",
        "division",
        "district",
        "total_amount",
        "created_at",
    )
    list_filter = ("division", "district", "created_at")
    search_fields = ("representative__name",)
    inlines = [SaleItemInline]
    readonly_fields = ("total_amount", "created_at")