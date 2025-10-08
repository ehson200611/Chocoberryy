# chocoberryapp/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import os

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return self.email

def product_image_path(instance, filename):
    return f'products/product_{instance.id}/{filename}'

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, default='Strawberries')
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    is_popular = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk is None and self.image:
            super().save(*args, **kwargs)
            if self.image:
                ext = self.image.name.split('.')[-1]
                self.image.name = f'products/product_{self.id}/image.{ext}'
                super().save(update_fields=['image'])
        else:
            super().save(*args, **kwargs)

class Location(models.Model):
    name = models.CharField(max_length=200, default="Chocoberry TJK")
    address = models.CharField(max_length=300)
    hours = models.CharField(max_length=100)
    hours_tajik = models.CharField(max_length=100, default="10:00 - 23:00 ҳар рӯз")
    phone = models.CharField(max_length=50)
    map_embed = models.TextField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class ContactInquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.price