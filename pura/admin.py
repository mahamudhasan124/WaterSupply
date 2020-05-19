from django.contrib import admin
from .models import Customer, Staff, Order, Cost

admin.site.register(Customer)
admin.site.register(Staff)
admin.site.register(Order)
admin.site.register(Cost)
