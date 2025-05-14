from django.contrib import admin

from app.models import Order, Product, OrderProduct

admin.site.register(Order)
admin.site.register(Product)
admin.site.register(OrderProduct)

