# Generated by Django 4.2.16 on 2024-10-30 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0016_userservicemodel_service_subscription_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicesmodel',
            name='service',
            field=models.CharField(choices=[('1', 'Patient Management'), ('2', 'School Management')], max_length=254),
        ),
    ]
