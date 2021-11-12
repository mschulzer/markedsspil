# Generated by Django 3.2.8 on 2021-11-05 11:59

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0012_auto_20211103_0951'),
    ]

    operations = [
        migrations.AddField(
            model_name='market',
            name='gamma',
            field=models.DecimalField(decimal_places=2, max_digits=14, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
    ]