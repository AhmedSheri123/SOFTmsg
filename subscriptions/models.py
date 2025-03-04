from django.db import models

# Create your models here.


SubscriptionsTheemChoices = (
    ('primary', 'primary'),
    ('secondary', 'secondary'),
    ('success', 'success'),
    ('danger', 'danger'),
    ('warning', 'warning'),
    ('info', 'info'),
    ('light', 'light'),
    ('dark', 'dark'),
)

CurrencyChoices = (
    ("SAR", "ريال سعودي"),
    ("USD", "دولار"),
    ("EUR", "يورو"),
)

plan_type_choices = [
    ('premium', 'Premium'),
    ('pro', 'PRO'),
    ('basic', 'Basic'),
]

plan_scope_choices = [
    ('1', 'Monthly'),
    ('2', 'Yearly')
]


def get_discont_original_price_and_saved_money(price, discont):
    orginal = None
    if price and discont:
        orginal = (price/ (100-discont))*100
        return int(orginal), int(orginal-price)
    return orginal, None

class HRSubscriptionsModel(models.Model):
    title = models.CharField(max_length=255, verbose_name='العنوان')
    subtitle = models.TextField(verbose_name='العنوان الفرعي')
    ico = models.ImageField(upload_to='subscription/ico/', blank=True)

    Theem = models.CharField(max_length=255, choices=SubscriptionsTheemChoices, null=True, verbose_name='الثيم')
    plan_type = models.CharField(max_length=255, choices=plan_type_choices, null=True, verbose_name='نو الاشتراك')

    number_of_days = models.IntegerField(default=30, verbose_name='عدد الأيام')

    price_monthly = models.DecimalField(max_digits=6, null=True, decimal_places=2, verbose_name='السعر')
    discont_monthly = models.IntegerField(default=0, null=True, verbose_name='خصم')

    price_yearly = models.DecimalField(max_digits=6, null=True, decimal_places=2, verbose_name='السعر')
    discont_yearly = models.IntegerField(default=0, null=True, verbose_name='خصم')

    currency = models.CharField(max_length=250, choices=CurrencyChoices, default='USD', null=True, verbose_name='العملة')


    # حدود المستخدمين
    number_of_employees = models.IntegerField(default=4, verbose_name='عدد الموظفين')
    number_of_managers = models.IntegerField(default=1, verbose_name='عدد المدراء')

    # ميزات الاشتراك المتعلقة بالموارد البشرية
    manage_employee = models.BooleanField(default=False, verbose_name='إدارة الموظفين')
    manage_recruitment = models.BooleanField(default=False, verbose_name='إدارة التوظيف')
    manage_onboarding = models.BooleanField(default=False, verbose_name='إدارة التدريب والاختبارات')
    manage_attendance = models.BooleanField(default=False, verbose_name='إدارة الحضور')
    payroll_management = models.BooleanField(default=False, verbose_name='إدارة الرواتب')
    leave_management = models.BooleanField(default=False, verbose_name='إدارة الإجازات')
    manage_assets = models.BooleanField(default=False, verbose_name='إدارة الأصول')
    pms_management = models.BooleanField(default=False, verbose_name='إدارة الأداء')
    manage_Offboarding = models.BooleanField(default=False, verbose_name='إدارة الخروج')
    manage_helpdesk = models.BooleanField(default=False, verbose_name='إدارة الدعم الفني')

    # تقارير إضافية متعلقة بالموارد البشرية
    employee_attendance_report = models.BooleanField(default=False, verbose_name='تقرير حضور الموظفين')
    employee_salary_report = models.BooleanField(default=False, verbose_name='تقرير رواتب الموظفين')
    employee_leave_report = models.BooleanField(default=False, verbose_name='تقرير إجازات الموظفين')
    performance_review_report = models.BooleanField(default=False, verbose_name='تقرير مراجعة الأداء')

    # إشعارات عبر البريد الإلكتروني أو الرسائل النصية
    send_email_notifications = models.BooleanField(default=False, verbose_name='إرسال إشعارات عبر البريد الإلكتروني')

    live_chat_with_support = models.BooleanField(default=False, verbose_name='دردشة مباشرة مع الدعم الفني')

    
    is_enabled = models.BooleanField(default=True, verbose_name='هل الاشتراك قابل للشراء')

    creation_date = models.DateTimeField(null=True, verbose_name="تاريخ الانشاء")

    def __str__(self):
        return str(self.title)
        

    def get_plans_Info(id=None):
        subscriptions_data = []
        subscriptions = HRSubscriptionsModel.objects.filter(is_enabled=True)
        
        if id:
            subscriptions = subscriptions.filter(id=id)
        
        def get_price_data(price, discount):
            original_price, saved_price = get_discont_original_price_and_saved_money(price, discount)
            return {
                "value": price,
                "orignal_price": original_price,
                "save_value": saved_price,
                "discont": discount
            }

        def get_field_data(field_name):
            return {
                "name": subscription._meta.get_field(field_name).verbose_name.title(),
                "type": "bool" if isinstance(getattr(subscription, field_name), bool) else "num",
                "value": getattr(subscription, field_name)
            }
        
        for subscription in subscriptions:
            data = {
                'id': subscription.id,
                'title': subscription.title,
                'subtitle': subscription.subtitle,
                'theme': {
                    "type": subscription.plan_type,
                    "theme": subscription.Theem
                },
                'price': {
                    "monthly": get_price_data(subscription.price_monthly, subscription.discont_monthly),
                    "yearly": get_price_data(subscription.price_yearly, subscription.discont_yearly)
                },
                'features': [
                    get_field_data(field) for field in [
                        'number_of_employees', 'manage_employee', 'manage_recruitment', 'manage_onboarding',
                        'manage_attendance', 'payroll_management', 'leave_management', 'manage_assets',
                        'pms_management', 'manage_Offboarding', 'manage_helpdesk', 'employee_attendance_report',
                        'employee_salary_report', 'employee_leave_report', 'performance_review_report',
                        'send_email_notifications', 'live_chat_with_support'
                    ]
                ]
            }
            subscriptions_data.append(data)

        return subscriptions_data
