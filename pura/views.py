from datetime import date,timedelta, datetime
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
from django.shortcuts import redirect


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
    return redirect('landing')


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
    staffs = Staff.objects.all().order_by('id')

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
        return redirect('/customer')

    context = {'item': customer}
    return render(request, 'pura/delete.html', context)


@login_required(login_url='login')
def customer_details(request, pk):
    customer_details = Customer.objects.get(id=pk)
    customer_orders = Order.objects.filter(customer_id=pk).order_by('-created')
    today = datetime.today()
    orders = Order.objects.filter(customer_id=pk,created__month=today.month, created__year=today.year)
    today = datetime.today()
    monthly_order = Order.objects.filter(customer_id=pk,created__month=today.month, created__year=today.year)
    customer_monthly_jar_given = monthly_order.aggregate(sum=Sum('jar_given')).get('sum') or 0
    customer_monthly_total = customer_monthly_jar_given * customer_details.jar_rate
    context = {'customer_details': customer_details, 'customer_orders': customer_orders,'orders':orders, 'customer_monthly_total':customer_monthly_total, }
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
    customers_col1, customers_col2 = customers[::2], customers[1::2]
    today = datetime.today().date()
    bar_find = datetime.today()
    bar = bar_find.strftime('%A')

    context = {'customers_col1': customers_col1,
               'customers_col2': customers_col2,
               'staff': staff, 'today': today,
               'delivery': delivery,
               'bar':bar,
               }
    return render(request, 'pura/delivery.html', context)

@login_required(login_url='login')
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

    context = {'form': form, 'orders': orders,}
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
    today = datetime.today().date()
    order = Order.objects.get(id=pk)
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

@login_required(login_url='login')
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

@login_required(login_url='login')
def account(request, year_month=None):
    staff_number = Staff.objects.all().count()

    customer_number = Customer.objects.all().count()

    if year_month:
        # 202011
        year = int(year_month / 100)
        month = int(year_month % 100)
        time = datetime(year, month, 1)
    else:
        time = datetime.today()

    monthly_order = Order.objects.filter(created__month=time.month, created__year=time.year)

    jar_given = monthly_order.aggregate(sum=Sum('jar_given')).get('sum') or 0
    jar_collect = monthly_order.aggregate(sum=Sum('jar_collect')).get('sum') or 0
    tk_collect = monthly_order.aggregate(sum=Sum('tk_collect')).get('sum') or 0

    total_taka = 0
    for order in monthly_order:
        total_taka += order.customer_id.jar_rate * order.jar_given

    monthly_order = Customer.objects.filter(created__month=time.month, created__year=time.year)
    #tk_previous_due = monthly_order.aggregate(sum=Sum('tk_previous_due')).get('sum') or 0
    #jar_previous_due = monthly_order.aggregate(sum=Sum('jar_previous_due')).get('sum') or 0
    tk_previous_due = total_taka - tk_collect
    jar_previous_due = jar_given - jar_collect

    monthly_result = {
        "jar_given": jar_given,
        "jar_collect": jar_collect,
        "tk_collect": tk_collect,
        "tk_previous_due": tk_previous_due,
        "jar_previous_due": jar_previous_due,
        "total_taka": total_taka,
    }

    cost = Cost.objects.filter(created__month=time.month, created__year=time.year)
    others_total = 0
    for c in cost:
        others_total += c.cost_amount

    staffs = Staff.objects.all()
    staff_total = 0
    for staff in staffs:
        staff_total += staff.salary

    total_cost = staff_total + others_total
    profit = tk_collect - total_cost
    previous_month = (time.replace(day=1) - timedelta(days=1)).strftime("%Y%m")
    next_month = (time.replace(day=28) + timedelta(days=5)).strftime("%Y%m")
    month = time.strftime('%B')
    staffs = Staff.objects.all()
    staffs_info = Staff.objects.all().filter()

    staffs_overview_list = []
    for st in staffs:
        s = st.get_staff_monthly_calculation(year_month=year_month)
        staff_overview = {
            'name': st.name,
            'jar_given': s['jar_given'],
            'jar_collect': s['jar_collect'],
            'jar_due':s['jar_due'],
            'total_taka': s['total_taka'],
            'tk_collect': s['tk_collect'],
            'tk_due':s['tk_due'],
        }
        staffs_overview_list.append(staff_overview)



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
        'staffs_overview_list':staffs_overview_list,

        'previous_month': f'/account/{previous_month}/',
        'next_month': f'/account/{next_month}/',
        'month': month,
    }
    return render(request, 'pura/account.html', context)



def landing_page(request):
    customers = Customer.objects.all().order_by('id')

    context = {'customers':customers, }
    return render(request, 'pura/landing_page.html', context)


@login_required(login_url='login')
def customer_priority(request):
    onedaybefore = datetime.now() - timedelta(days=1)
    twodaybefore = datetime.now() - timedelta(days=2)
    threedaybefore = datetime.now() - timedelta(days=3)
    fourdaybefore = datetime.now() - timedelta(days=4)
    fivedaybefore = datetime.now() - timedelta(days=5)
    sixdaybefore = datetime.now() - timedelta(days=6)

    onec = Order.objects.filter(created__gte=onedaybefore).order_by('customer_id')
    twoc = Order.objects.filter(created__lte=twodaybefore,created__gte=twodaybefore).order_by('customer_id')
    threec = Order.objects.filter(created__lte=threedaybefore,created__gte=threedaybefore).order_by('customer_id')
    fourc = Order.objects.filter(created__lte=fourdaybefore,created__gte=fourdaybefore).order_by('customer_id')
    fivec = Order.objects.filter(created__lte=fivedaybefore,created__gte=fivedaybefore).order_by('customer_id')
    sixc = Order.objects.filter(created__lte=sixdaybefore).order_by('customer_id')

    one = []
    two = []
    three = []
    four = []
    five = []
    six = []

    for o in onec:
        if o.customer_id not in one:
            one.append(o.customer_id)

    for t in twoc:
        if t.customer_id not in two and t.customer_id not in one:
            two.append(t.customer_id)


    for t in threec:
        if t.customer_id not in three and t.customer_id not in two and t.customer_id not in one:
            two.append(t.customer_id)


    for f in fourc:
        if f.customer_id not in four and f.customer_id not in three and f.customer_id not in two and f.customer_id not in one:
            two.append(f.customer_id)


    for t in fivec:
        if t.customer_id not in five and t.customer_id not in four and t.customer_id not in three and t.customer_id not in two and t.customer_id not in one:
            two.append(t.customer_id)

    for t in sixc:
        if t.customer_id not in six and t.customer_id not in five and t.customer_id not in four and t.customer_id not in three and t.customer_id not in two and t.customer_id not in one:
            six.append(t.customer_id)



    context = {'one':one,'two':two,'three':three,'four':four,'five':five,'six':six,}
    return render(request,'pura/customer_priority.html',context)

