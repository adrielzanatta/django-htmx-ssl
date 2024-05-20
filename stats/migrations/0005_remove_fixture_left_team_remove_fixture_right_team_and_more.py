# Generated by Django 5.0.6 on 2024-05-19 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0004_seasonplayerstatistics_draws_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fixture',
            name='left_team',
        ),
        migrations.RemoveField(
            model_name='fixture',
            name='right_team',
        ),
        migrations.RemoveField(
            model_name='team',
            name='name',
        ),
        migrations.AddField(
            model_name='team',
            name='side_name',
            field=models.IntegerField(choices=[(1, 'Team A'), (2, 'Team B')], default='0'),
        ),
    ]
