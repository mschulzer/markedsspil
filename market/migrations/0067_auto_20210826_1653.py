# Generated by Django 3.2.4 on 2021-08-26 14:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0066_trader_round_joined'),
    ]

    operations = [
        migrations.AddField(
            model_name='roundstat',
            name='avg_balance',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='market',
            name='max_rounds',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
