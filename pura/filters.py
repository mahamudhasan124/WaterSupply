import django_filters
from django_filters import CharFilter
from .models import *

class CustomerFilter(django_filters.FilterSet):
    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['updated','tk_previous_due','jar_previous_due','name','mobile','email','address', 'jar_rate', 'supply_begin','created','staff','']






