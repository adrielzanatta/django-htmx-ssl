# Generated by Django 5.0.6 on 2024-05-21 15:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0010_fixture_goal_balance_fixture_winner_team_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='fixture',
        ),
    ]
