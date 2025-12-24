from django.db import models

from apps.models import Warehouse

from django.utils.translation import gettext as _


class Category(models.Model):
    name = models.CharField(max_length=100)
    warehouse = models.ForeignKey('apps.Warehouse', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


from django.db import models


class Product(models.Model):
    class Units(models.TextChoices):
        KG = 'kg', 'Kilogram'
        L = 'l', 'Litr'
        PCS = 'pcs', 'Dona'
        M = 'm', 'Metr'

    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='products/')
    unit = models.CharField(max_length=40, choices=Units.choices, default=Units.KG)
    created_at = models.DateTimeField(auto_now_add=True)
    min_quantity = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    description = models.TextField()
    warehouse = models.ForeignKey(
        'apps.Warehouse',
        on_delete=models.SET_NULL,
        related_name='products',
        null=True,
        blank=True
    )
    categories = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('sku', 'warehouse')

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def investment(self):
        return self.quantity * self.base_price

    def kassa(self):
        if self.discount_price > 0:
            return self.quantity * self.discount_price
        return self.quantity * self.price

    @property
    def status(self) -> str:
        if self.quantity == 0:
            return "Tugagan"
        elif self.quantity < self.min_quantity:
            return "Kam qolgan"
        else:
            return "Yaxshi"


class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} {self.product.unit}"


class Order(models.Model):
    warehouse = models.ForeignKey('apps.Warehouse', on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)

    products = models.ManyToManyField(Product, through='OrderItem')


class ProductTransfer(models.Model):
    from_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='transfers_out'
    )
    to_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='transfers_in'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    transferred_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} from {self.from_warehouse.name} to {self.to_warehouse.name}"

    class Meta:
        ordering = ['-transferred_at']
        verbose_name = "Product Transfer"
        verbose_name_plural = "Product Transfers"


class Transactions(models.Model):
    class Status(models.TextChoices):
        INTRO = "intro", _("Intro")
        EXIT = "exit", _("Exit")

    name = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.INTRO)
    created_at = models.DateTimeField(auto_now_add=True)
    warehouse = models.ForeignKey('apps.Warehouse', on_delete=models.CASCADE, related_name='transactions')
