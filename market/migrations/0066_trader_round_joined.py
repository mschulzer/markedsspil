# Generated by Django 3.2.4 on 2021-08-24 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0065_remove_market_game_over'),
    ]

    operations = [
        migrations.AddField(
            model_name='trader',
            name='round_joined',
            field=models.IntegerField(default=0),
        ),
    ]