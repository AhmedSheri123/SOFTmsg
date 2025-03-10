from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from .forms import (AddUserServiceModelForm, PatientManagementHospital, SchoolManagementProfile, HRManagementProfile)
from .models import (ServicesModel, UserServiceModel, ServicePaymentOrderModel)
from django.contrib import messages
from django.conf import settings
import json, requests
from .payment import addInvoice, getInvoice
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from paypal.standard.forms import PayPalPaymentsForm
from decimal import Decimal
from subscriptions.models import HRSubscriptionsModel
from .tools import data_base, hr_docker, deploy
from .projects_setting import hr_setting
import os

# Create your views here.
PatientManagementURL = settings.PATIENT_MANAGEMENT_WEB_SERVER_URL
SchoolManagementURL = settings.SCHOOL_MANAGEMENT_WEB_SERVER_URL
HRManagementURL = settings.HR_MANAGEMENT_WEB_SERVER_URL
HR_MANAGEMENT_SYSTEM_SRC_PATH = settings.HR_MANAGEMENT_SYSTEM_SRC_PATH
DEFAULT_HR_DB_USER = settings.DEFAULT_HR_DB_USER
DEFAULT_HR_DB_PASS = settings.DEFAULT_HR_DB_PASS
PAYPAL_RECIVVER_EMAIL = settings.PAYPAL_RECIVVER_EMAIL

def Home(request):
    user = request.user
    user_services = UserServiceModel.objects.filter(user=user)
    orders = ServicePaymentOrderModel.objects.filter(user_service__user=user)
    active_user_services = user_services.filter(progress='4')
    copmlited_orders = orders.filter(progress='3')
    uncopmlited_orders = orders.exclude(progress='3')
    
    context = {
        'active_user_services': active_user_services.count(),
        'copmlited_orders': copmlited_orders.count(),
        'uncopmlited_orders': uncopmlited_orders.count(),
        'orders':orders
    }
    return render(request, 'dashboard/home.html', context)

def MyServices(request):
    user_services = UserServiceModel.objects.filter(user=request.user).order_by('-id')
    return render(request, 'dashboard/services/MyServices.html', {'user_services':user_services})

def DeletePatientManagementService(request, id):
    user_services = UserServiceModel.objects.get(id=id)
    service_user_id = user_services.service_user_id
    if service_user_id:
        res = requests.get(f'{PatientManagementURL}/en/accounts/DeletePatientManagementAPI/{service_user_id}')
        if res.status_code == 200:
            data = res.json()
            if data.get('status'):
                user_services.delete()
    else:user_services.delete()
    return redirect('MyServices')


def DeleteSchoolManagementService(request, id):
    user_services = UserServiceModel.objects.get(id=id)
    service_user_id = user_services.service_user_id
    if service_user_id:
        res = requests.get(f'{SchoolManagementURL}/en/DeleteSchoolManagementAPI/{service_user_id}')

        if res.status_code == 200:
            data = res.json()
            if data.get('status'):
                user_services.delete()
    else:user_services.delete()
    return redirect('MyServices')

def DeleteHRManagementService(request, id):
    user_services = UserServiceModel.objects.get(id=id)
    service_user_id = user_services.service_user_id
    app_name = user_services.subdomain
    if service_user_id:
        hr_docker.remove_container(app_name)
        data_base.remove_database(db_name=app_name, user=DEFAULT_HR_DB_USER, password=DEFAULT_HR_DB_PASS, host='77.37.122.10', port='5434')
        hr_docker.remove_hr_service(app_name)
        if os.name == "posix":
            deploy.remove_file(f'/etc/nginx/sites-enabled/{app_name}.conf')
        user_services.delete()
    else:user_services.delete()
    messages.success(request, 'Project has been removed')
    return redirect('MyServices')

def DeleteService(request, id):
    user_services = UserServiceModel.objects.get(id=id)
    service_user_id = user_services.service_user_id
    selected_service = user_services.service.service
    if service_user_id:
        if selected_service == '1':
            return DeletePatientManagementService(request, id)
        elif selected_service == '2':
            return DeleteSchoolManagementService(request, id)
        elif selected_service == '3':
            return DeleteHRManagementService(request, id)
    else:
        user_services.delete()
        return redirect('MyServices')

def ResetPasswordService(request, id):
    if request.method == 'POST':
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password == password2:
            data = {
                'password':password
            }
            res_data = {}
            user_services = UserServiceModel.objects.get(id=id)
            service_user_id = user_services.service_user_id
            selected_service = user_services.service.service


            if service_user_id:
                if selected_service == '1':
                    res = requests.post(f'{PatientManagementURL}/en/accounts/ResetPasswordAPI/{service_user_id}', data=data)
                elif selected_service == '2':
                    res = requests.post(f'{SchoolManagementURL}/en/ResetPasswordAPI/{service_user_id}', data=data)
                elif selected_service == '3':
                    response_data, exit_code = hr_docker.change_user_password(user_services.subdomain, service_user_id, password)
                    if exit_code == 0:
                        res_data['status'] = True
                    else:
                        res_data['status'] = False

                if not res_data:
                    if res.status_code == 200:
                        res_data = res.json()
                    else:messages.error(request, 'error on trying connect to server please call support')

                if res_data.get('status'):
                    messages.success(request, 'Password has been changed successfully')
                else:
                    messages.error(request, 'Password not changed got some errors, please call support')
            else:messages.error(request, 'error on changing password please call support')
        else:messages.error(request, 'new password field and repeat new password field not same')
    return redirect('ViewService', id)


def check_is_deployed(request, user_service_id):
    user_service = UserServiceModel.objects.get(id=user_service_id)
    # r = hr_docker.check_migrations(user_service.subdomain)
    url = f'http://77.37.122.10:{user_service.system_port}/'
    r = False
    try:
        res = requests.get(url)
        if res.status_code == 200 or res.status_code == 301 or res.status_code == 302:
            r = True
    except:
        pass
    return JsonResponse({'success':r}, safe=False)

def buliding_waiting_page(request, user_service_id):
    check_is_deployed_url = reverse('check_is_deployed', kwargs={'user_service_id':user_service_id})
    success_page = reverse('AddHRManagementSettings', kwargs={'id':user_service_id})
    return render(request, 'dashboard/bulding/buliding_waiting_page.html', {'check_is_deployed_url':check_is_deployed_url, 'success_page':success_page})

def DeployHRSystem(request, user_service):
    if user_service.system_progress == '3':
        return redirect('buliding_waiting_page', user_service.id)

    project_name = 'horilla'
    domain = 'softmsg.com'
    subdomain = user_service.subdomain if user_service.subdomain else user_service.get_unique_subdomain(user_service.project_name)
    port = user_service.system_port if user_service.system_port else user_service.get_avarible_port
    user_service.subdomain = subdomain
    user_service.system_port = port
    static_folder_name = 'staticfiles'

    #create database for project
    creating_database = data_base.create_database(db_name=subdomain, user=DEFAULT_HR_DB_USER, password=DEFAULT_HR_DB_PASS, host='77.37.122.10', port='5434')
    print('adding service')
    hr_docker.add_hr_service(subdomain, port)
    print('runing container')
    hr_docker.compose_up(subdomain)
    # hr_docker.run_container(subdomain, port)
    print('success')
    
    if os.name == "posix":
        #create nginx for app
        deploying = deploy.create_nginx_config(static_folder_name, subdomain, port, domain)
        deploy.restart_services()
    if creating_database:
        user_service.system_progress = '3'
        user_service.save()
        return redirect('buliding_waiting_page', user_service.id)
    else:
        user_service.system_progress = '4'
        user_service.save()
        messages.error(request, 'حدث خطاء اثناء بناء النظام')
        return redirect('MyServices')
    
    
    

def UserServiceCreationProgress(request, id):
    user_service = UserServiceModel.objects.get(id=id)
    progress = user_service.progress
    if progress == '1': return redirect('AddService')
    elif progress == '2': return redirect('ServicePlans', id)
    elif progress == '3':
        if user_service.service.service == '1':
            return redirect('AddPatientManagementSettings', id)
        elif user_service.service.service == '2':
            return redirect('AddSchoolManagementSettings', id)
        elif user_service.service.service == '3':
            return DeployHRSystem(request, user_service)
    elif progress == '4':
        return redirect('ViewService', id)
    return redirect('MyServices')

def AddService(request):
    service_info_url = reverse('GetServiceInfo')
    form = AddUserServiceModelForm()
    if request.method == 'POST':
        form = AddUserServiceModelForm(data=request.POST)
        if form.is_valid():
            user_service = form.save(commit=False)
            user_service.user = request.user
            user_service.progress = '2'
            user_service.save()

            return redirect('UserServiceCreationProgress', user_service.id)
    return render(request, 'dashboard/services/AddService.html', {'form':form, 'service_info_url':service_info_url})


def ServicePlans(request, id):
    user_service = UserServiceModel.objects.get(id=id)
    plans_data = []
    selected_service = user_service.service.service
    if selected_service == '1':
        res = requests.get(f'{PatientManagementURL}/en/accounts/GetSubscriptionsPlanInfoAPI')
        if res.status_code == 200:
            plans_data = res.json()

    elif selected_service == '2':
        res = requests.get(f'{SchoolManagementURL}/en/GetSubscriptionsPlanInfoAPI')
        if res.status_code == 200:
            plans_data = res.json()

    elif selected_service == '3':
        plans_data = HRSubscriptionsModel.get_plans_Info()

    if request.method == 'POST':
        plan_scope = request.POST.get('plan_scope')
        service_id = request.POST.get('selected_service_id')
        
        subscription_data = {}
        for plan in plans_data:
            if str(plan.get('id')) == service_id:
                subscription_data = plan
                break
        price = None
        if plan_scope == '1':
            price = Decimal(plan['price']['monthly']['value'])
        elif plan_scope == '2':
            price = Decimal(plan['price']['yearly']['value'])

        order = ServicePaymentOrderModel.objects.create(user_service=user_service)
        order.title = subscription_data.get('title')
        order.subscription_id = service_id
        order.progress_paid_plan_scope = plan_scope
        order.save()
        if price <= 0:
            return EnableServiceSubscription(request, order.orderID)
        # user_service.progress_paid_plan_id = service_id
        # user_service.progress_paid_plan_scope = plan_scope
        # user_service.progress = '3'
        # user_service.save()
        return redirect('ServicePayment', order.orderID)

    return render(request, 'dashboard/services/ServicePlans.html', {'plans_data':plans_data, 'user_service':user_service})

def ServicePayment(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    subscription_id = order.subscription_id

    selected_service = order.user_service.service.service
    plans_data = []
    if selected_service == '1':
        res = requests.get(f'{PatientManagementURL}/en/accounts/GetSubscriptionsPlanInfoAPI?id={subscription_id}')
        if res.status_code == 200:
            plans_data = res.json()

    elif selected_service == '2':
        res = requests.get(f'{SchoolManagementURL}/en/GetSubscriptionsPlanInfoAPI?id={subscription_id}')
        if res.status_code == 200:
            plans_data = res.json()

    if plans_data:
        plan = plans_data[0]
        ser_title = plan.get('title')
        ser_disc = plan.get('subtitle')
        price = None
        if order.progress_paid_plan_scope == '1':
            price = plan['price']['monthly']['value']
        elif order.progress_paid_plan_scope == '2':
            price = plan['price']['yearly']['value']

        user = request.user
        userprofile = user.userprofile
        index_url = request.build_absolute_uri('/')
        index_url = index_url.rsplit('/', 1)[0]              
        cancelUrl= index_url + reverse('CancellingOrder', kwargs={'orderID': orderID})
        PayPalCallBackUrl= index_url + reverse('PaypalCheckPaymentProcess', kwargs={'secret': order.order_secret})
        # PayPal Payment
        paypal_dict = {
            "business": PAYPAL_RECIVVER_EMAIL,
            "amount": price,
            "item_name": ser_title,
            "invoice": orderID,
            "currency_code": 'USD',
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return": PayPalCallBackUrl,
            "cancel_return": cancelUrl,
            "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
        }
        paypal_form = PayPalPaymentsForm(initial=paypal_dict)

        if request.method == 'POST':

            
            clientName = user.first_name + ' ' + user.last_name
            total_price_amount = price
            email = user.email
            phone = userprofile.phone_number
            callBackUrl= index_url + reverse('checkPaymentProcess', kwargs={'orderID': orderID})

            p_res = addInvoice(orderID, total_price_amount, email, phone, clientName, ser_title, ser_disc, callBackUrl, cancelUrl, 'USD')
            if p_res.get('success'):
                order.transactionNo = p_res.get('transactionNo')
                order.save()
                return HttpResponseRedirect(p_res.get('url'))

        return render(request, 'dashboard/services/payment/pay.html', {'plan':plan, 'price':price, 'paypal_form':paypal_form})

    return redirect('ServicePlans', order.user_service.id)

def UpgradeOrRenewServiceSubscription(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    user_service = UserServiceModel.objects.get(id=order.user_service.id)
    print(user_service.service.service)
    if user_service.service.service == '1':
        return PatientManagementRenewSubscription(request, orderID)
    elif user_service.service.service == '2':
        return SchoolManagementRenewSubscription(request, orderID)
    elif user_service.service.service == '3':
        return HRManagementRenewSubscription(request, orderID)
    

def EnableServiceSubscription(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    user_service = UserServiceModel.objects.get(id=order.user_service.id)
    if user_service.progress != '4':
        user_service.service_subscription_id = order.subscription_id
        user_service.plan_scope = order.progress_paid_plan_scope
        user_service.progress = '3'
        order.progress = '3'
        
        user_service.save()
        order.save()
        return redirect('UserServiceCreationProgress', user_service.id)
    else:
        order.progress = '2'
        return redirect('UpgradeOrRenewServiceSubscription', orderID)

def checkPaymentProcess(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    r = getInvoice(order.transactionNo)
    if r.get('success'):
        if r.get('orderStatus') == 'Paid':
            return EnableServiceSubscription(request, order.id)
    return redirect('index')

def PaypalCheckPaymentProcess(request, secret):
    orders = ServicePaymentOrderModel.objects.filter(order_secret=secret)
    if orders.exists():
        order = orders.first()
        return EnableServiceSubscription(request, order.id)
    return redirect('index')

def PatientManagementRenewSubscription(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    user_service = UserServiceModel.objects.get(id=order.user_service.id)
    post_data = {}
    post_data['subscription_id'] = order.subscription_id
    post_data['subscription_scope'] = order.progress_paid_plan_scope

    res = requests.post(f'{PatientManagementURL}/en/accounts/RenewSubscription/{user_service.service_user_id}', data=post_data)

    if res.status_code == 200:
        res_data = res.json()
        if res_data.get('status'):
            user_service.service_subscription_id = order.subscription_id
            user_service.plan_scope = order.progress_paid_plan_scope
            order.progress = '3'
            user_service.save()
            order.save()
            messages.success(request, 'تم تجديد الاشتراك بنجاح')
            return redirect('UserServiceCreationProgress', user_service.id)
        else:
            error_msgs = res_data.get('msgs')
            if error_msgs:
                for msg in error_msgs:
                    messages.error(request, msg)
    return

def SchoolManagementRenewSubscription(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    user_service = UserServiceModel.objects.get(id=order.user_service.id)
    post_data = {}
    post_data['subscription_id'] = order.subscription_id
    post_data['subscription_scope'] = order.progress_paid_plan_scope

    res = requests.post(f'{SchoolManagementURL}/en/RenewSubscription/{user_service.service_user_id}', data=post_data)

    if res.status_code == 200:
        res_data = res.json()
        if res_data.get('status'):
            user_service.service_subscription_id = order.subscription_id
            user_service.plan_scope = order.progress_paid_plan_scope
            order.progress = '3'
            user_service.save()
            order.save()
            messages.success(request, 'تم تجديد الاشتراك بنجاح')
            return redirect('UserServiceCreationProgress', user_service.id)
        else:
            error_msgs = res_data.get('msgs')
            if error_msgs:
                for msg in error_msgs:
                    messages.error(request, msg)
    return


def HRManagementRenewSubscription(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    user_service = UserServiceModel.objects.get(id=order.user_service.id)
    post_data = {}
    post_data['subscription_id'] = order.subscription_id
    post_data['subscription_scope'] = order.progress_paid_plan_scope

    hr_docker.add_subscription(user_service.subdomain, user_service.plan_scope, HRSubscriptionsModel.objects.get(id=user_service.service_subscription_id))

    user_service.service_subscription_id = order.subscription_id
    user_service.plan_scope = order.progress_paid_plan_scope
    order.progress = '3'
    user_service.save()
    order.save()
    messages.success(request, 'تم تجديد الاشتراك بنجاح')
    return redirect('UserServiceCreationProgress', user_service.id)

    return

def AddPatientManagementSettings(request, id):
    user = request.user
    user_service = UserServiceModel.objects.get(id=id)
    
    form = PatientManagementHospital()
    form.initial['first_name'] = user.first_name
    form.initial['last_name'] = user.last_name
    form.initial['number'] = user.userprofile.phone_number

    if request.method == 'POST':
        form = PatientManagementHospital(data=request.POST)
        if form.is_valid():
            post_data = form.cleaned_data
            post_data['subscription_id'] = user_service.service_subscription_id
            post_data['subscription_scope'] = user_service.plan_scope

            res = requests.post(f'{PatientManagementURL}/en/accounts/AddHospitalsByAPI', data=post_data)
            if res.status_code == 200:
                res_data = res.json()
                
                if res_data.get('status'):
                    service_user_id = res_data.get('user_id')
                    user_service.service_user_id=service_user_id
                    user_service.progress = '4'
                    user_service.save()
                    return redirect('UserServiceCreationProgress', user_service.id)
                else:
                    error_msgs = res_data.get('msgs')
                    if error_msgs:
                        for msg in error_msgs:
                            messages.error(request, msg)
    return render(request, 'dashboard/services/AddServiceSettings/AddPatientManagementSettings.html', {'form':form})

def AddSchoolManagementSettings(request, id):
    user = request.user
    user_service = UserServiceModel.objects.get(id=id)
    
    form = SchoolManagementProfile()
    form.initial['first_name'] = user.first_name
    form.initial['last_name'] = user.last_name
    form.initial['number'] = user.userprofile.phone_number


    if request.method == 'POST':
        form = SchoolManagementProfile(data=request.POST)
        if form.is_valid():
            post_data = form.cleaned_data
            post_data['subscription_id'] = user_service.service_subscription_id
            post_data['subscription_scope'] = user_service.plan_scope

            res = requests.post(f'{SchoolManagementURL}/en/AddHospitalsByAPI', data=post_data)
            if res.status_code == 200:
                res_data = res.json()
                if res_data.get('status'):
                    service_user_id = res_data.get('user_id')
                    user_service.service_user_id=service_user_id
                    user_service.progress = '4'
                    user_service.save()
                    return redirect('UserServiceCreationProgress', user_service.id)
                else:
                    error_msgs = res_data.get('msgs')
                    if error_msgs:
                        for msg in error_msgs:
                            messages.error(request, msg)
    return render(request, 'dashboard/services/AddServiceSettings/AddSchoolManagementSettings.html', {'form':form})


def AddHRManagementSettings(request, id):
    user = request.user
    user_service = UserServiceModel.objects.get(id=id)
    
    form = HRManagementProfile()
    form.initial['first_name'] = user.first_name
    form.initial['last_name'] = user.last_name
    form.initial['number'] = user.userprofile.phone_number
    form.initial['email'] = user.email
    
    if request.method == 'POST':
        form = HRManagementProfile(data=request.POST)
        if form.is_valid():
            post_data = form.cleaned_data
            post_data['subscription_id'] = user_service.service_subscription_id
            post_data['subscription_scope'] = user_service.plan_scope
            hr_docker.add_subscription(user_service.subdomain, user_service.plan_scope, HRSubscriptionsModel.objects.get(id=user_service.service_subscription_id))
            add_user = hr_docker.add_user(user_service.subdomain, post_data['first_name'], post_data['last_name'], post_data['username'], post_data['password'], post_data['email'], post_data['number'])
            data, exit_code = add_user
            if exit_code != 0:
                return JsonResponse({'success': False, 'errors': data})
            user_id = data.get('user_id')
            user_service.service_user_id=user_id
            user_service.progress = '4'
            user_service.save()
            return JsonResponse({'success': True, 'redirect_url': reverse('UserServiceCreationProgress', kwargs={'id':user_service.id})})
        return JsonResponse({'success': False, 'errors': None})
    return render(request, 'dashboard/services/AddServiceSettings/AddHRManagementSettings.html', {'form':form})

def ViewPatientManagementService(request, id):
    user_service = UserServiceModel.objects.get(id=id)
    plans_data = []
    res = requests.get(f'{PatientManagementURL}/en/accounts/GetPatientManagementInfo/{user_service.service_user_id}')
    plans_res = requests.get(f'{PatientManagementURL}/en/accounts/GetSubscriptionsPlanInfoAPI?id={user_service.service_subscription_id}')
    if plans_res.status_code == 200:
        plans_data = plans_res.json()
    if res.status_code == 200:
        data = res.json()
        if data:
            data['user_service'] = user_service
            return render(request, 'dashboard/services/viewService/ViewPatientManagementService.html', {'data':data, 'plans_data':plans_data, 'PatientManagementURL':PatientManagementURL})
    return redirect('MyServices')


def ViewSchoolManagementService(request, id):
    user_service = UserServiceModel.objects.get(id=id)
    plans_data = []
    res = requests.get(f'{SchoolManagementURL}/en/GetSchoolManagementInfo/{user_service.service_user_id}')
    plans_res = requests.get(f'{SchoolManagementURL}/en/GetSubscriptionsPlanInfoAPI?id={user_service.service_subscription_id}')
    if plans_res.status_code == 200:
        plans_data = plans_res.json()
    if res.status_code == 200:
        data = res.json()
        if data:
            data['user_service'] = user_service
            return render(request, 'dashboard/services/viewService/ViewSchoolManagementService.html', {'data':data, 'plans_data':plans_data, 'SchoolManagementURL':SchoolManagementURL})
    return redirect('MyServices')


def ViewHRManagementService(request, id):
    user_service = UserServiceModel.objects.get(id=id)
    plans_data = []
    data = {}
    
    plans_data = HRSubscriptionsModel.get_plans_Info(id=user_service.service_subscription_id)
    res, exit_code = hr_docker.get_system_info(user_service.subdomain, user_service.service_user_id)
    if exit_code == 0:
        data = res
    else:
        messages.error(request, res)
    data['user_service'] = user_service
    return render(request, 'dashboard/services/viewService/ViewHRManagementService.html', {'data':data, 'plans_data':plans_data, 'HRManagementURL':HRManagementURL})
    return redirect('MyServices')


def ViewService(request, id):
    
    user_service = UserServiceModel.objects.get(id=id)
    if user_service.service.service == '1':
        return ViewPatientManagementService(request, id)
    elif user_service.service.service == '2':
        return ViewSchoolManagementService(request, id)
    elif user_service.service.service == '3':
        return ViewHRManagementService(request, id)

def GetServiceInfo(request):
    id = request.GET.get('id')
    if id:
        service = ServicesModel.objects.get(id=id)
        data = {
            'status':True,
            'id':service.id,
            'title':service.title,
            'subtitle':service.sub_title,
        }
        return JsonResponse(data, safe=False)
    return JsonResponse({'status':False}, safe=False)



def MyOrders(request):
    orders = ServicePaymentOrderModel.objects.filter(user_service__user=request.user).order_by('-id')
    return render(request, 'dashboard/orders/MyOrders.html', {'orders':orders})

def DeleteOrder(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    order.delete()
    return redirect('MyOrders')

def CancellingOrder(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    order.progress = '4'
    order.save()
    return redirect('ServicePlans', order.user_service.id)