# Generated by Django 4.2.11 on 2024-08-16 18:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('euro', '0010_cupteams'),
    ]

    operations = [
        migrations.CreateModel(
            name='CupDraw',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('g_id', models.IntegerField()),
                ('c_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='euro.cup')),
                ('t_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='euro.ntteam')),
            ],
        ),
    ]
