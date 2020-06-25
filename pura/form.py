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
        today = datetime.today().date()
        order = Order.objects.all().filter(created__gte=today, created__lte=today)
        if jar_given == 0 and jar_collect==0 and tk_collect==0:
            raise forms.ValidationError('All value can not be 0')

    def clean_customer_id(self):
        customer = self.cleaned_data['customer_id']
        today = datetime.today().date()
        ordered_customer = Order.objects.filter(created__lte=today, created__gte=today)

        if customer in ordered_customer:
            raise forms.ValidationError('Already used ID')


'''        
    def clean_test_data(self):
        data = self.cleaned_data.get('customer_id')
        today = datetime.today().date()
        order = Order.objects.all().filter(created__gte=today,created__lte=today)
        print(order)
        order_id = order['customer_id']

        if data in order_id:
            raise forms.ValidationError('ID already used')
        return data
'''
'''
    def clean_customer_id(self):
        
'''

'''
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        # already_order_customer_list = get_daily_order_customer_list()
        customer_id = Customer.objects.all().exclude(id__in=get_daily_order_customer_list())
        self.fields['customer_id'].queryset = customer_id
'''

class CostForm(ModelForm):
    class Meta:
        model = Cost
        fields = '__all__'

