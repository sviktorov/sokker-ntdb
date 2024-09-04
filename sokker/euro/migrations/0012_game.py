# Generated by Django 4.2.11 on 2024-08-16 18:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('euro', '0011_cupdraw'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('g_status', models.CharField(max_length=50)),
                ('group_id', models.IntegerField()),
                ('goals_home', models.IntegerField()),
                ('goals_away', models.IntegerField()),
                ('cup_round', models.CharField(max_length=50)),
                ('matchID', models.CharField(max_length=255)),
                ('playoff_position', models.CharField(blank=True, max_length=50, null=True)),
                ('c_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='euro.cup')),
                ('t_id_h', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_team', to='euro.ntteam')),
                ('t_id_v', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='away_team', to='euro.ntteam')),
            ],
        ),
    ]