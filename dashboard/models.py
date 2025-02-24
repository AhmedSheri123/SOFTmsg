from django.db import models
from django.contrib.auth.models import User
import random, string, datetime
from django.utils.translation import gettext_lazy as _ 
# Create your models here.

def payOrderCodeGen(N = 4):
    res = ''.join(random.choices(string.digits, k=N))
    order = ServicePaymentOrderModel.objects.filter(orderID=res)
    if order.exists():
        res = payOrderCodeGen(N+1)
    return 'o' + str(res)

def payOrderSecretCodeGen():
    N = 99
    res = ''.join(random.choices((string.digits+string.ascii_letters), k=N))
    return str(res)

services_choices = [
    ('1', _('Patient Management')),
    ('2', _('School Management')),
    ('3', _('HR Management')),
]

plan_scope_choices = [
    ('1', _('Monthly')),
    ('2', _('Yearly'))
]

order_progress_choices = [
    ('1', _('Pending')),
    ('2', _('Paid')),
    ('3', _('Complited')),
    ('4', _('Cancelled'))
]

user_service_progress_choices = [
    ('1', _('Create Project')),
    ('2', _('Choose Plan')),
    ('3', _('Project Settings')),
    ('4', _('Complited'),
)]

class ServicesModel(models.Model):
    title = models.CharField(max_length=254, verbose_name=_("Service Title"))
    sub_title = models.TextField(verbose_name=_("Subtitle"))
    service = models.CharField(max_length=254, choices=services_choices, verbose_name=_("Service"))

    creation_datetime = models.DateTimeField(auto_now_add=True, verbose_name=_("Creation Date"))

    class Meta:
        verbose_name = _("Service Model")
        verbose_name_plural = _("Service Models")

    def __str__(self):
        return str(self.get_service_display())


class UserServiceModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name=_("User"))
    project_name = models.CharField(max_length=254, null=True, verbose_name=_("Project Name"))
    service = models.ForeignKey(ServicesModel, on_delete=models.CASCADE, null=True, verbose_name=_("Service"))
    progress = models.CharField(max_length=254, choices=user_service_progress_choices, null=True, verbose_name=_("Progress"))

    service_subscription_id = models.CharField(max_length=254, null=True, verbose_name=_("Service Subscription ID"))
    service_user_id = models.CharField(max_length=254, null=True, verbose_name=_("Service User ID"))
    service_subscription_date = models.CharField(max_length=254, null=True, verbose_name=_("Service Subscription Date"))
    plan_scope = models.CharField(max_length=254, choices=plan_scope_choices, null=True, verbose_name=_("Plan Scope"))

    creation_datetime = models.DateTimeField(auto_now_add=True, verbose_name=_("Creation Date"))

    class Meta:
        verbose_name = _("User Service Model")
        verbose_name_plural = _("User Service Models")

    def __str__(self):
        return str(self.project_name)

    @property
    def remaining_subscription(self):
        subscription_date = self.service_subscription_date
        if subscription_date:
            subscription_days = 30 if self.plan_scope else 365
            subscription_end_date = (datetime.timedelta(days=subscription_days) + subscription_date) - subscription_date


class ServicePaymentOrderModel(models.Model):
    user_service = models.ForeignKey(UserServiceModel, on_delete=models.SET_NULL, null=True, verbose_name=_("User Service"))
    title = models.CharField(max_length=250, null=True, verbose_name=_("Full Name"))
    subscription_id = models.CharField(max_length=254, null=True, verbose_name=_("Subscription ID"))
    progress_paid_plan_scope = models.CharField(max_length=254, choices=plan_scope_choices, null=True, verbose_name=_("Paid Plan Scope"))
    orderID = models.CharField(max_length=250, default=payOrderCodeGen, null=True, verbose_name=_("Order ID"))
    order_secret = models.CharField(max_length=254, default=payOrderSecretCodeGen, null=True, verbose_name=_("Order Secret Code"))
    transactionNo = models.CharField(max_length=250, null=True, verbose_name=_("Transaction Number"))
    progress = models.CharField(max_length=254, default='1', choices=order_progress_choices, null=True, verbose_name=_("Order Progress"))
    creation_date = models.DateTimeField(null=True, verbose_name=_("Creation Date"))

    class Meta:
        verbose_name = _("Service Payment Order Model")
        verbose_name_plural = _("Service Payment Order Models")
