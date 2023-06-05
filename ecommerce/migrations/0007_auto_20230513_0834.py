# Generated by Django 3.2 on 2023-05-13 01:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0006_orderdetail_discount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdetail',
            name='amount',
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='discount',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.DO_NOTHING, to='ecommerce.coupon'),
        ),
    ]