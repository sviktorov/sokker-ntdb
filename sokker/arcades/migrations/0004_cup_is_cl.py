# Generated by Django 4.2.11 on 2024-12-23 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arcades', '0003_cupcategory_alter_game_t_id_h_alter_game_t_id_v_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cup',
            name='is_cl',
            field=models.BooleanField(default=False),
        ),
    ]
