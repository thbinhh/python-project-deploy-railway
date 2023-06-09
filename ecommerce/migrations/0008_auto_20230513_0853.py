# Generated by Django 3.2 on 2023-05-13 01:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ecommerce', '0007_auto_20230513_0834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetail',
            name='discount',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ecommerce.coupon'),
        ),
        migrations.CreateModel(
            name='CouponUsed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ecommerce.coupon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'coupon_used',
                'managed': True,
            },
        ),
    ]
