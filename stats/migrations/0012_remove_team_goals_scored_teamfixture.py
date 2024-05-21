# Generated by Django 5.0.6 on 2024-05-21 16:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0011_remove_team_fixture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='goals_scored',
        ),
        migrations.CreateModel(
            name='TeamFixture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goals_scored', models.PositiveSmallIntegerField(default=0)),
                ('fixture', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams_fixture', to='stats.fixture')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams_fixture', to='stats.team')),
            ],
        ),
    ]