# Generated by Django 4.2.11 on 2024-05-23 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sokker_base', '0005_alter_country_currency_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]