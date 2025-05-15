import uuid
from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):

    class Currency(models.TextChoices):
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

    def get_total_amount(self):
        """Calculate the total amount of the order"""
        total = sum(
            item.product.price * item.quantity
            for item in self.orderproduct_set.all()
        )
        return total

    def get_total_amount_in_tiyins(self):
        """Convert total amount to tiyins for Payme (100 tiyins = 1 UZS)"""
        total = self.get_total_amount()

        return int(total * 100)

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order.id} - Product: {self.product.name}"

class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        FAILED = 'FAILED', 'Failed'
        CANCELED = 'CANCELED', 'Canceled'
        REFUNDED = 'REFUNDED', 'Refunded'

    class PaymentProvider(models.TextChoices):
        PAYME = 'PAYME', 'Payme'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_id = models.CharField(max_length=255, unique=True)
    provider = models.CharField(max_length=10, choices=PaymentProvider.choices, default=PaymentProvider.PAYME)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    provider_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    provider_transaction_time = models.BigIntegerField(blank=True, null=True)
    provider_payment_data = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment #{self.payment_id} for Order #{self.order.id}"

    @classmethod
    def create_for_order(cls, order):
        """Create a new payment for an order"""
        payment = cls(
            order=order,
            payment_id=str(uuid.uuid4()),
            amount=order.get_total_amount(),
            status=cls.PaymentStatus.PENDING
        )
        payment.save()
        return payment

    def get_amount_in_tiyins(self):
        """Convert payment amount to tiyins for Payme"""
        return int(self.amount * 100)