# Generated by Django 4.2 on 2023-05-17 14:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0014_shop_shop_image_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='cate_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='ecommerce.category'),
            preserve_default=False,
        ),
    ]