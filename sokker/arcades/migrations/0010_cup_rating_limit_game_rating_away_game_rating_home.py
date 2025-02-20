# Generated by Django 4.2.11 on 2025-01-25 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arcades', '0009_alter_game_g_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='cup',
            name='rating_limit',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='rating_away',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='rating_home',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]
