# Generated by Django 4.2 on 2023-07-23 10:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_alter_videostatus_host'),
    ]

    operations = [
        migrations.CreateModel(
            name='Nofification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Type', models.CharField(max_length=100, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('From', models.ManyToManyField(related_name='From', to=settings.AUTH_USER_MODEL)),
                ('Room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.room')),
                ('To', models.ManyToManyField(related_name='To', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='VideoStatus',
        ),
    ]