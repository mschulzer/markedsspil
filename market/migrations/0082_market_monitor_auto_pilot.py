# Generated by Django 3.2.7 on 2021-10-07 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0081_trader_auto_play'),
    ]

    operations = [
        migrations.AddField(
            model_name='market',
            name='monitor_auto_pilot',
            field=models.BooleanField(default=False),
        ),
    ]