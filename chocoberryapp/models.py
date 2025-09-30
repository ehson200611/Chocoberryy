from django.db import models
import os

def product_image_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/products/product_<id>/<filename>
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
        # If this is a new product and has an image
        if self.pk is None and self.image:
            super().save(*args, **kwargs)
            # Update the image path to include the product ID
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