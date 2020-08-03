from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'

class StaffForm(ModelForm):
    class Meta:
        model = Staff
        fields = '__all__'


class CreateUserFormWithEmail(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email','password1','password2']


def get_daily_order_customer_list():
    today = datetime.today().date()
    return Order.objects.filter(created__lte=today, created__gte=today).values_list('customer_id', flat=True)


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        # fields = ['id','customer_id','jar_given','jar_collect','tk_collect']

    def clean(self):
        cleaned_data = super().clean()
        jar_given = cleaned_data.get('jar_given')
        jar_collect = cleaned_data.get('jar_collect')
        tk_collect = cleaned_data.get('tk_collect')
        if jar_given == 0 and jar_collect==0 and tk_collect==0:
            raise forms.ValidationError('All value can not be 0')
        #today = datetime.today().date()
        #ordered_customer = Order.objects.filter(created=today, customer_id=cleaned_data.get('customer_id'))
        #if ordered_customer:
        #    raise forms.ValidationError('Already used ID')
        return cleaned_data


class CostForm(ModelForm):
    class Meta:
        model = Cost
        fields = '__all__'

