# Generated by Django 4.1.3 on 2023-03-30 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0002_alter_sessionpool_sessionid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='entity_super',
            new_name='super_administraor',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='system_super',
            new_name='system_administrator',
        ),
        migrations.AddField(
            model_name='user',
            name='asset_administrator',
            field=models.IntegerField(default=1),
        ),
    ]
