# Generated by Django 4.2.16 on 2025-03-03 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HRSubscriptionsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='العنوان')),
                ('subtitle', models.TextField(verbose_name='العنوان الفرعي')),
                ('ico', models.ImageField(blank=True, upload_to='subscription/ico/')),
                ('Theem', models.CharField(choices=[('primary', 'primary'), ('secondary', 'secondary'), ('success', 'success'), ('danger', 'danger'), ('warning', 'warning'), ('info', 'info'), ('light', 'light'), ('dark', 'dark')], max_length=255, null=True, verbose_name='الثيم')),
                ('plan_type', models.CharField(choices=[('premium', 'Premium'), ('pro', 'PRO'), ('basic', 'Basic')], max_length=255, null=True, verbose_name='نو الاشتراك')),
                ('number_of_days', models.IntegerField(default=30, verbose_name='عدد الأيام')),
                ('price_monthly', models.DecimalField(decimal_places=2, max_digits=6, null=True, verbose_name='السعر')),
                ('discont_monthly', models.IntegerField(default=0, null=True, verbose_name='خصم')),
                ('price_yearly', models.DecimalField(decimal_places=2, max_digits=6, null=True, verbose_name='السعر')),
                ('discont_yearly', models.IntegerField(default=0, null=True, verbose_name='خصم')),
                ('currency', models.CharField(choices=[('SAR', 'ريال سعودي'), ('USD', 'دولار'), ('EUR', 'يورو')], default='USD', max_length=250, null=True, verbose_name='العملة')),
                ('number_of_employees', models.IntegerField(default=4, verbose_name='عدد الموظفين')),
                ('number_of_managers', models.IntegerField(default=1, verbose_name='عدد المدراء')),
                ('manage_employee', models.BooleanField(default=False, verbose_name='إدارة الموظفين')),
                ('manage_recruitment', models.BooleanField(default=False, verbose_name='إدارة التوظيف')),
                ('manage_onboarding', models.BooleanField(default=False, verbose_name='إدارة التدريب والاختبارات')),
                ('manage_attendance', models.BooleanField(default=False, verbose_name='إدارة الحضور')),
                ('payroll_management', models.BooleanField(default=False, verbose_name='إدارة الرواتب')),
                ('leave_management', models.BooleanField(default=False, verbose_name='إدارة الإجازات')),
                ('manage_assets', models.BooleanField(default=False, verbose_name='إدارة الأصول')),
                ('pms_management', models.BooleanField(default=False, verbose_name='إدارة الأداء')),
                ('manage_Offboarding', models.BooleanField(default=False, verbose_name='إدارة الخروج')),
                ('manage_helpdesk', models.BooleanField(default=False, verbose_name='إدارة الدعم الفني')),
                ('employee_attendance_report', models.BooleanField(default=False, verbose_name='تقرير حضور الموظفين')),
                ('employee_salary_report', models.BooleanField(default=False, verbose_name='تقرير رواتب الموظفين')),
                ('employee_leave_report', models.BooleanField(default=False, verbose_name='تقرير إجازات الموظفين')),
                ('performance_review_report', models.BooleanField(default=False, verbose_name='تقرير مراجعة الأداء')),
                ('send_email_notifications', models.BooleanField(default=False, verbose_name='إرسال إشعارات عبر البريد الإلكتروني')),
                ('live_chat_with_support', models.BooleanField(default=False, verbose_name='دردشة مباشرة مع الدعم الفني')),
                ('is_enabled', models.BooleanField(default=True, verbose_name='هل الاشتراك قابل للشراء')),
                ('creation_date', models.DateTimeField(null=True, verbose_name='تاريخ الانشاء')),
            ],
        ),
    ]
