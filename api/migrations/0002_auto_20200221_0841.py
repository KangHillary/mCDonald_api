# Generated by Django 2.2.10 on 2020-02-21 08:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sessionkey',
            old_name='user',
            new_name='customer',
        ),
    ]
