from django.contrib import admin
from .models import ServicesModel, UserServiceModel, ServicePaymentOrderModel
# Register your models here.
admin.site.register(ServicesModel)
admin.site.register(UserServiceModel)
admin.site.register(ServicePaymentOrderModel)