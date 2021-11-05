# Generated by Django 3.2.8 on 2021-11-03 08:51

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0011_alter_market_alpha'),
    ]

    operations = [
        migrations.AlterField(
            model_name='market',
            name='beta',
            field=models.DecimalField(decimal_places=2, max_digits=14, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='market',
            name='theta',
            field=models.DecimalField(decimal_places=2, max_digits=14, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
    ]