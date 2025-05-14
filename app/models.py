from django.contrib.auth.models import User
from django.db import models

class Product(models.Model):

    class Currency(models.TextChoices):
        USD = 'USD', 'US Dollar'
        EUR = 'EUR', 'Euro'
        UZS = 'UZS', 'Uzbek Soʻm'

    name = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    currency = models.CharField(max_length=3, choices=Currency.choices)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Order(models.Model):

    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        FAILED = 'FAILED', 'Failed'
        SHIPPED = 'SHIPPED', 'Shipped'
        CANCELED = 'CANCELED', 'Canceled'
        COMPLETED = 'COMPLETED', 'Completed'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product, through='OrderProduct')
    status = models.CharField(choices=OrderStatus.choices, default=OrderStatus.PENDING, max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id}"

class OrderProduct(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.product.id} - Product: {self.product.name}"

class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        FAILED = 'FAILED', 'Failed'
        CANCELED = 'CANCELED', 'Canceled'



