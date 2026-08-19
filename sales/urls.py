from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),

    path(
        "sales/",
        views.sales_entry,
        name="sales_entry"
    ),

    path(
        "sales/submit/",
        views.submit_sale,
        name="submit_sale"
    ),

    path(
        "sales/success/<int:sale_id>/",
        views.sale_success,
        name="sale_success"
    ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),
]