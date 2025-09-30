from django.contrib import admin
from .models import Product, Location, ContactInquiry

admin.site.register(Product)
admin.site.register(Location)
admin.site.register(ContactInquiry)