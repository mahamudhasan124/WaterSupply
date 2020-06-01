from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import *
from django.utils.timezone import datetime
from .form import *
from .filters import CustomerFilter
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                messages.info(request, 'Username OR Password is incorrect')

    context = {}
    return render(request, 'pura/login.html', context)


def logout_admin(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def register_page(request):
    form = CreateUserFormWithEmail()
    if request.method == 'POST':
        form = CreateUserFormWithEmail(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form, }
    return render(request, 'pura/register.html', context)


@login_required(login_url='login')
def home(request):
    staffs = Staff.objects.all()
    today = datetime.today()
    monthly_order = Order.objects.filter(created__month=today.month, created__year=today.year)

    jar_given = monthly_order.aggregate(sum=Sum('jar_given')).get('sum') or 0
    jar_collect = monthly_order.aggregate(sum=Sum('jar_collect')).get('sum') or 0
    tk_collect = monthly_order.aggregate(sum=Sum('tk_collect')).get('sum') or 0

    total_taka = 0
    for order in monthly_order:
        total_taka += order.customer_id.jar_rate * order.jar_given

    monthly_order = Customer.objects.filter(created__month=today.month, created__year=today.year)
    tk_previous_due = monthly_order.aggregate(sum=Sum('tk_previous_due')).get('sum') or 0
    jar_previous_due = monthly_order.aggregate(sum=Sum('jar_previous_due')).get('sum') or 0
    # tk_previous_due = total_taka - tk_collect
    # jar_previous_due = jar_given - jar_collect

    monthly_result = {
        "jar_given": jar_given,
        "jar_collect": jar_collect,
        "tk_collect": tk_collect,
        "tk_previous_due": tk_previous_due,
        "jar_previous_due": jar_previous_due,
        "total_taka": total_taka,
    }

    daily_order = Order.objects.filter(created__gte=today, created__lte=today)
    jar_given = daily_order.aggregate(sum=Sum('jar_given')).get('sum') or 0
    jar_collect = daily_order.aggregate(sum=Sum('jar_collect')).get('sum') or 0
    tk_collect = daily_order.aggregate(sum=Sum('tk_collect')).get('sum') or 0

    total_taka = 0
    for order in daily_order:
        total_taka += order.customer_id.jar_rate * order.jar_given

    daily_order = Customer.objects.filter(created__gte=today, created__lte=today)
    # tk_previous_due = daily_order.aggregate(sum=Sum('tk_previous_due')).get('sum') or 0
    # jar_previous_due = daily_order.aggregate(sum=Sum('jar_previous_due')).get('sum') or 0
    tk_previous_due = total_taka - tk_collect
    jar_previous_due = jar_given - jar_collect

    daily_result = {
        "jar_given": jar_given,
        "jar_collect": jar_collect,
        "tk_collect": tk_collect,
        "tk_previous_due": tk_previous_due,
        "jar_previous_due": jar_previous_due,
        "total_taka": total_taka,
    }

    context = {
        'staffs': staffs,
        'daily_result': daily_result,
        'monthly_result': monthly_result,

    }
    return render(request, 'pura/dashboard.html', context)


@login_required(login_url='login')
def staff(request):
    staffs = Staff.objects.all()

    context = {'staffs': staffs}
    return render(request, 'pura/staff.html', context)


@login_required(login_url='login')
def customer(request):
    customers = Customer.objects.all().order_by('id')

    customer_filter = CustomerFilter(request.GET, queryset=customers)
    customers = customer_filter.qs

    context = {'customers': customers, 'customer_filter': customer_filter, }
    return render(request, 'pura/customer.html', context)


@login_required(login_url='login')
def add_customer(request):
    form = CustomerForm
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/customer')

    context = {'form': form, }
    return render(request, 'pura/customer_form.html', context)


@login_required(login_url='login')
def edit_customer(request, pk):
    customer = Customer.objects.get(id=pk)
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('/customer')

    context = {'form': form, }
    return render(request, 'pura/customer_form.html', context)


@login_required(login_url='login')
def delete_customer(request, pk):
    customer = Customer.objects.get(id=pk)
    if request.method == 'POST':
        customer.delete()
        customer.save()
        return redirect('/customer')

    context = {'item': customer}
    return render(request, 'pura/delete.html', context)


@login_required(login_url='login')
def customer_details(request, pk):
    customer_details = Customer.objects.get(id=pk)
    customer_orders = Order.objects.filter(customer_id=pk)
    context = {'customer_details': customer_details, 'customer_orders': customer_orders}
    return render(request, 'pura/customer_details.html', context)


@login_required(login_url='login')
def add_staff(request):
    form = StaffForm()
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/staff')

    context = {'form': form, }
    return render(request, 'pura/staff_form.html', context)


@login_required(login_url='login')
def edit_staff(request, pk):
    staff = Staff.objects.get(id=pk)
    form = StaffForm(instance=staff)

    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            return redirect('/staff')

    context = {'form': form, }
    return render(request, 'pura/staff_form.html', context)


@login_required(login_url='login')
def delivery(request, pk):
    customers = Customer.objects.filter(staff_id=pk).order_by('id')
    staff = Staff.objects.get(id=pk)
    customers_col1 = customers[:len(customers)//2]
    customers_col2 = customers[len(customers)//2:]
    today = datetime.today().date()

    context = {'customers_col1': customers_col1,'customers_col2': customers_col2, 'staff': staff, 'today': today, 'delivery': delivery}
    return render(request, 'pura/delivery.html', context)


def staff_details_today(request, pk):
    today = datetime.today().date()
    total_jar_given_today = Order.objects.all().filter(customer_id__staff_id=pk, created__gte=today,
                                                       created__lte=today).aggregate(sum('jar_given'))

    context = {
        'total_jar_given_today': total_jar_given_today,

    }
    return render(request, 'pura/staff.html', context)


@login_required(login_url='login')
def add_order(request):
    form = OrderForm
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/order')

    today = datetime.today().date()
    orders = Order.objects.filter(created__lte=today, created__gte=today).order_by('customer_id')

    context = {'form': form, 'orders': orders, 'all_order': all_order}
    return render(request, 'pura/order.html', context)


'''
def edit_order(request,pk):
    order = get_object_or_404(Order, pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save(commit=False)
            order.save()
            return redirect('/order')
    else:
        form = OrderForm(instance=order)
        template = 'pura/order.html'
        context = {'form':form}

    return redirect(request, template,context)

'''


@login_required(login_url='login')
def edit_order(request, pk):
    order = Order.objects.get(customer_id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/order')

    context = {'form': form, }
    return render(request, 'pura/order.html', context)


@login_required(login_url='login')
def all_order(request):
    all_order = Order.objects.all().order_by('-created','customer_id')

    context = {'all_order': all_order,}
    return render(request, 'pura/all_order.html', context)


def guideline(request):
    return render(request, 'pura/guideline.html')


@login_required(login_url='login')
def cost(request):
    form = CostForm
    if request.method == 'POST':
        form = CostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/cost')

    today = datetime.today().date()
    cost = Cost.objects.filter(created__month=today.month, created__year=today.year)
    others_total=0
    for c in cost:
        others_total += c.cost_amount

    staffs = Staff.objects.all()
    staff_total = 0
    for staff in staffs:
        staff_total += staff.salary

    total = staff_total + others_total

    context = {'form': form, 'cost':cost, 'others_total':others_total, 'staff_total':staff_total,
               'total':total}
    return render(request, 'pura/cost.html', context)


@login_required(login_url='login')
def edit_cost(request, pk):
    cost_edit = Cost.objects.get(cost_id=pk)
    form = CostForm(instance=cost_edit)

    if request.method == 'POST':
        form = CostForm(request.POST, instance=cost_edit)
        if form.is_valid():
            form.save()
            return redirect('/cost')

    context = {'form': form}
    return render(request, 'pura/cost.html', context)


def account(request):
    staff_number = Staff.objects.all().count()
    staffs = Staff.objects.all()
    customer_number = Customer.objects.all().count()

    today = datetime.today()
    monthly_order = Order.objects.filter(created__month=today.month, created__year=today.year)

    jar_given = monthly_order.aggregate(sum=Sum('jar_given')).get('sum') or 0
    jar_collect = monthly_order.aggregate(sum=Sum('jar_collect')).get('sum') or 0
    tk_collect = monthly_order.aggregate(sum=Sum('tk_collect')).get('sum') or 0

    total_taka = 0
    for order in monthly_order:
        total_taka += order.customer_id.jar_rate * order.jar_given

    monthly_order = Customer.objects.filter(created__month=today.month, created__year=today.year)
    tk_previous_due = monthly_order.aggregate(sum=Sum('tk_previous_due')).get('sum') or 0
    jar_previous_due = monthly_order.aggregate(sum=Sum('jar_previous_due')).get('sum') or 0
    # tk_previous_due = total_taka - tk_collect
    # jar_previous_due = jar_given - jar_collect

    monthly_result = {
        "jar_given": jar_given,
        "jar_collect": jar_collect,
        "tk_collect": tk_collect,
        "tk_previous_due": tk_previous_due,
        "jar_previous_due": jar_previous_due,
        "total_taka": total_taka,
    }

    cost = Cost.objects.filter(created__month=today.month, created__year=today.year)
    others_total = 0
    for c in cost:
        others_total += c.cost_amount

    staffs = Staff.objects.all()
    staff_total = 0
    for staff in staffs:
        staff_total += staff.salary

    total_cost = staff_total + others_total
    profit = tk_collect - total_cost


    context = {
        'staff_number':staff_number,
        'staffs':staffs,
        'customer_number':customer_number,
        'monthly_result':monthly_result,
        'others_total':others_total,
        'staff_total':staff_total,
        'total_cost':total_cost,
        'cost':cost,
        'profit':profit,

    }
    return render(request, 'pura/account.html', context)


