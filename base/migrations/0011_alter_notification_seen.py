# Generated by Django 4.2 on 2023-07-23 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_notification_seen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='Seen',
            field=models.BooleanField(default=False),
        ),
    ]
