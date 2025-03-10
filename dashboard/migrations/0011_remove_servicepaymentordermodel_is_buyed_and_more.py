# Generated by Django 4.2.16 on 2024-09-24 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_servicepaymentordermodel_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servicepaymentordermodel',
            name='is_buyed',
        ),
        migrations.AddField(
            model_name='servicepaymentordermodel',
            name='progress',
            field=models.CharField(choices=[('1', 'Pending'), ('2', 'Complited'), ('3', 'Cancelled')], max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='servicepaymentordermodel',
            name='title',
            field=models.CharField(max_length=250, null=True, verbose_name='الاسم الثلاثي'),
        ),
        migrations.AlterField(
            model_name='userservicemodel',
            name='progress',
            field=models.CharField(choices=[('1', 'Create Project'), ('2', 'Choose Plan'), ('3', 'Project Settings'), ('4', 'Complited')], max_length=254, null=True),
        ),
    ]
