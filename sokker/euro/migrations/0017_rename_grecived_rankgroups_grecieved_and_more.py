# Generated by Django 4.2.11 on 2024-08-16 19:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('euro', '0016_rename_t_id_h_rankgroups_t_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rankgroups',
            old_name='grecived',
            new_name='grecieved',
        ),
        migrations.RenameField(
            model_name='rankgroups',
            old_name='gscorered',
            new_name='gscored',
        ),
    ]
