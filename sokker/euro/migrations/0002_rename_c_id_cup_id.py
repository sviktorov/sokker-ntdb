# Generated by Django 4.2.11 on 2024-08-16 16:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('euro', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cup',
            old_name='c_id',
            new_name='id',
        ),
    ]
