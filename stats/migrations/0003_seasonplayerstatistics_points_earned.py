# Generated by Django 5.0.6 on 2024-05-16 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0002_rename_playerseasonstatistics_seasonplayerstatistics_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='seasonplayerstatistics',
            name='points_earned',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]