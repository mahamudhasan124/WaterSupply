from django.db import models
from datetime import datetime, date, timedelta,time
from django.db.models import Sum


class Staff(models.Model):
    id = models.IntegerField(primary_key=True, blank=False)
    name = models.CharField(max_length=255, blank=False)
    mobile = models.IntegerField(blank=False)
    email = models.EmailField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    salary = models.IntegerField(blank=False)
    duty_Area = models.CharField(max_length=255, null=True)
    job_Started = models.DateField("Date format: year-month-day", auto_now_add=False, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

    def get_staff_daily_calculation(self):
        today = datetime.today()
        staff_all_orders = Order.objects.filter(customer_id__staff__id=self.id, created__gte=today, created__lte=today)
        jar_given = staff_all_orders.aggregate(sum=Sum('jar_given')).get('sum') or 0
        jar_collect = staff_all_orders.aggregate(sum=Sum('jar_collect')).get('sum', 0) or 0
        tk_collect = staff_all_orders.aggregate(sum=Sum('tk_collect')).get('sum', 0) or 0

        total_taka = 0
        for order in staff_all_orders:
            total_taka += order.customer_id.jar_rate * order.jar_given

        staff_all_customer = Customer.objects.filter(staff__id=self.id)
        tk_previous_due = staff_all_customer.aggregate(sum=Sum('tk_previous_due')).get('sum', 0) or 0
        jar_previous_due = staff_all_customer.aggregate(sum=Sum('jar_previous_due')).get('sum', 0) or 0
        #tk_previous_due = total_taka - tk_collect
        #jar_previous_due = jar_given - jar_collect

        result = {
            "jar_given": jar_given,
            "jar_collect": jar_collect,
            "tk_collect": tk_collect,
            "tk_previous_due": tk_previous_due,
            "jar_previous_due": jar_previous_due,
            "total_taka": total_taka,
        }
        return result

    def get_staff_monthly_calculation(self, year_month=None):
        if year_month:
            year = int(year_month / 100)
            month = int(year_month % 100)
            time = datetime(year, month, 1)
        else:
            time = datetime.today()

        staff_all_orders = Order.objects.filter(customer_id__staff__id=self.id, created__month=time.month,
                                                created__year=time.year)
        jar_given = staff_all_orders.aggregate(sum=Sum('jar_given')).get('sum', 0) or 0
        jar_collect = staff_all_orders.aggregate(sum=Sum('jar_collect')).get('sum', 0) or 0
        tk_collect = staff_all_orders.aggregate(sum=Sum('tk_collect')).get('sum', 0) or 0

        total_taka = 0
        for order in staff_all_orders:
            total_taka += order.customer_id.jar_rate * order.jar_given

        staff_all_customer = Customer.objects.filter(staff__id=self.id)
        tk_previous_due = staff_all_customer.aggregate(sum=Sum('tk_previous_due')).get('sum', 0) or 0
        jar_previous_due = staff_all_customer.aggregate(sum=Sum('jar_previous_due')).get('sum', 0) or 0
        tk_due = total_taka - tk_collect
        jar_due = jar_given - jar_collect

        result = {
            "jar_given": jar_given,
            "jar_collect": jar_collect,
            "tk_collect": tk_collect,
            "tk_previous_due": tk_previous_due,
            "jar_previous_due": jar_previous_due,
            "total_taka": total_taka,
            "tk_due":tk_due,
            "jar_due":jar_due,
        }
        return result


class Customer(models.Model):
    id = models.IntegerField(primary_key=True, blank=False)
    name = models.CharField(max_length=255, blank=False)
    mobile = models.IntegerField(blank=False)
    email = models.EmailField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    jar_rate = models.IntegerField(blank=False)
    staff = models.ForeignKey(Staff, blank=False, on_delete=models.CASCADE)
    supply_begin = models.DateField("Date format: year-month-date", max_length=255, blank=True, null=True)
    tk_previous_due = models.IntegerField(blank=True, null=True, default=0)
    jar_previous_due = models.IntegerField(blank=True, null=True, default=0)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        ordering = ('id',)

    # def total_bill(self):
    #     total_bill =

    def __str__(self):
        return str(self.id)


class Order(models.Model):
    customer_id = models.ForeignKey(Customer, null=True, on_delete=models.CASCADE)
    jar_given = models.IntegerField(blank=True, null=True, default=0)
    jar_collect = models.IntegerField(blank=True, null=True, default=0)
    tk_collect = models.IntegerField(blank=True, null=True, default=0)
    created = models.DateField(auto_now_add=True)



    def __str__(self):
        return str(self.customer_id)

    def save(self, *args, **kwargs):
        if not self.id:
            self.customer_id.jar_previous_due = self.customer_id.jar_previous_due + self.jar_given - \
                                                self.jar_collect
            self.customer_id.tk_previous_due = self.customer_id.tk_previous_due + \
                                               (self.jar_given * self.customer_id.jar_rate) - self.tk_collect
            self.customer_id.save()

        else:
            previous_total_jar = self.customer_id.jar_previous_due
            previous_total_tk = self.customer_id.tk_previous_due

            previous_order_obj = Order.objects.get(id=self.id)
            total_jar = previous_total_jar - previous_order_obj.jar_given + previous_order_obj.jar_collect
            total_bill = previous_total_tk - (previous_order_obj.jar_given * previous_order_obj.customer_id.jar_rate) + \
                         previous_order_obj.tk_collect

            self.customer_id.jar_previous_due = total_jar + self.jar_given - \
                                                self.jar_collect
            self.customer_id.tk_previous_due = total_bill + \
                                               (self.jar_given * self.customer_id.jar_rate) - self.tk_collect
            self.customer_id.save()

        super(Order, self).save(*args, **kwargs)

    def total_bill_today(self):
        total_bill_today = self.customer_id.jar_rate * self.jar_given
        return total_bill_today

    def jar_due_today(self):
        jar_due_today =  self.jar_given - self.jar_collect
        return jar_due_today

    def taka_due_today(self):
        tk_due_today = self.total_bill_today() - self.tk_collect
        return tk_due_today


class Cost(models.Model):
    cost_id = models.AutoField(primary_key=True)
    cost_details = models.CharField(max_length=255,blank=False)
    cost_amount = models.PositiveIntegerField(blank=False)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.cost_details


