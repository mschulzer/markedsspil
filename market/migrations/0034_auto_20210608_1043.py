# Generated by Django 3.1.11 on 2021-06-08 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0033_auto_20210607_1807'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='trade',
            constraint=models.UniqueConstraint(fields=('trader', 'round'), name='trader_and_round_unique_together'),
        ),
    ]