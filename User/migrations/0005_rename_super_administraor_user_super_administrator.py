# Generated by Django 4.1.3 on 2023-03-30 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0004_alter_user_asset_administrator'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='super_administraor',
            new_name='super_administrator',
        ),
    ]
