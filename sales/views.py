import json
from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    Division,
    District,
    Representative,
    TeaProduct,
    TeaPackage,
    Sale,
    SaleItem,
)


def home(request):
    return render(request, "home.html")


def sales_entry(request):

    divisions = list(
        Division.objects.values("id", "name")
    )

    districts = list(
        District.objects.values(
            "id",
            "name",
            "division_id"
        )
    )

    representatives = list(
        Representative.objects.filter(active=True).values(
            "id",
            "name",
            "employee_id",
            "district_id"
        )
    )

    products = list(
        TeaProduct.objects.values("id", "name")
    )

    packages = list(
        TeaPackage.objects.values(
            "id",
            "product_id",
            "weight_grams",
            "price"
        )
    )

    for package in packages:
        package["price"] = float(package["price"])

    context = {
        "divisions": divisions,
        "districts": districts,
        "representatives": representatives,
        "products": products,
        "packages": packages,
    }

    return render(request, "sales_entry.html", context)


@transaction.atomic
def submit_sale(request):

    if request.method != "POST":
        return redirect("sales_entry")

    representative_id = request.POST.get("representative_id")
    items_json = request.POST.get("items_json")

    if not representative_id or not items_json:
        messages.error(request, "Please complete the sales form.")
        return redirect("sales_entry")

    try:
        items = json.loads(items_json)
    except json.JSONDecodeError:
        messages.error(request, "Invalid sales data.")
        return redirect("sales_entry")

    if not items:
        messages.error(request, "Please add at least one product.")
        return redirect("sales_entry")

    representative = get_object_or_404(
        Representative.objects.select_related(
            "district__division"
        ),
        id=representative_id,
        active=True,
    )

    sale = Sale.objects.create(
        representative=representative,
        district=representative.district,
        division=representative.district.division,
        total_amount=Decimal("0"),
    )

    grand_total = Decimal("0")

    for item in items:

        product = get_object_or_404(
            TeaProduct,
            id=item.get("product_id")
        )

        package = get_object_or_404(
            TeaPackage,
            id=item.get("package_id"),
            product=product
        )

        quantity = int(item.get("quantity", 0))

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        unit_price = package.price
        total = unit_price * quantity

        SaleItem.objects.create(
            sale=sale,
            product=product,
            package=package,
            quantity=quantity,
            unit_price=unit_price,
            total=total,
        )

        grand_total += total

    sale.total_amount = grand_total
    sale.save(update_fields=["total_amount"])

    return redirect("sale_success", sale_id=sale.id)


def sale_success(request, sale_id):

    sale = get_object_or_404(
        Sale.objects.select_related(
            "representative",
            "division",
            "district",
        ).prefetch_related("items__product", "items__package"),
        id=sale_id
    )

    return render(
        request,
        "success.html",
        {"sale": sale}
    )


def dashboard(request):

    total_sales = Sale.objects.aggregate(
        total=Sum("total_amount")
    )["total"] or Decimal("0")

    total_transactions = Sale.objects.count()

    total_quantity = SaleItem.objects.aggregate(
        total=Sum("quantity")
    )["total"] or 0

    division_sales = list(
        Division.objects
        .annotate(total=Sum("sales__total_amount"))
        .values("name", "total")
        .order_by("-total")
    )

    for row in division_sales:
        row["total"] = float(row["total"] or 0)

    product_sales = list(
        TeaProduct.objects
        .annotate(total=Sum("sale_items__total"))
        .values("name", "total")
        .order_by("-total")
    )

    for row in product_sales:
        row["total"] = float(row["total"] or 0)

    representative_sales = list(
        Representative.objects
        .annotate(total=Sum("sales__total_amount"))
        .values(
            "name",
            "employee_id",
            "total"
        )
        .order_by("-total")
    )

    for row in representative_sales:
        row["total"] = float(row["total"] or 0)

    recent_sales = (
        Sale.objects
        .select_related(
            "representative",
            "division",
            "district",
        )
        .order_by("-created_at")[:10]
    )

    context = {
        "total_sales": total_sales,
        "total_transactions": total_transactions,
        "total_quantity": total_quantity,
        "division_sales": division_sales,
        "product_sales": product_sales,
        "representative_sales": representative_sales,
        "recent_sales": recent_sales,
    }

    return render(
        request,
        "dashboard.html",
        context
    )
