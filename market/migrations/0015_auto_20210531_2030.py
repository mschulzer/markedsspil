# Generated by Django 3.1.11 on 2021-05-31 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0014_auto_20210531_1954'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='unit_amount',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='trade',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]