from django.db import models


class Division(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class District(models.Model):
    division = models.ForeignKey(
        Division,
        on_delete=models.CASCADE,
        related_name="districts"
    )
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        unique_together = ("division", "name")

    def __str__(self):
        return f"{self.name} - {self.division.name}"


class Representative(models.Model):
    name = models.CharField(max_length=150)
    employee_id = models.CharField(max_length=50, unique=True)
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name="representatives"
    )
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.employee_id})"


class TeaProduct(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class TeaPackage(models.Model):
    product = models.ForeignKey(
        TeaProduct,
        on_delete=models.CASCADE,
        related_name="packages"
    )
    weight_grams = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["product", "weight_grams"]
        unique_together = ("product", "weight_grams")

    def __str__(self):
        return f"{self.product.name} - {self.weight_grams}g - ৳{self.price}"


class Sale(models.Model):
    representative = models.ForeignKey(
        Representative,
        on_delete=models.PROTECT,
        related_name="sales"
    )
    division = models.ForeignKey(
        Division,
        on_delete=models.PROTECT,
        related_name="sales"
    )
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name="sales"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Sale #{self.id} - ৳{self.total_amount}"


class SaleItem(models.Model):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        TeaProduct,
        on_delete=models.PROTECT,
        related_name="sale_items"
    )
    package = models.ForeignKey(
        TeaPackage,
        on_delete=models.PROTECT,
        related_name="sale_items"
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"