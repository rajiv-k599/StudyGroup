# Generated by Django 4.2 on 2023-07-01 08:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_remove_room_call_status_videostatus'),
    ]

    operations = [
        migrations.RenameField(
            model_name='videostatus',
            old_name='updated',
            new_name='created',
        ),
    ]
