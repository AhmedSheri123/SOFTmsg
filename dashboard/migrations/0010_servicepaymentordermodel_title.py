# Generated by Django 4.2.16 on 2024-09-24 17:11

import dashboard.libs
from django.db import migrations, models

import dashboard.models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_rename_userservice_servicepaymentordermodel_user_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicepaymentordermodel',
            name='title',
            field=models.CharField(default=dashboard.models.payOrderCodeGen, max_length=250, null=True, verbose_name='الاسم الثلاثي'),
        ),
    ]
