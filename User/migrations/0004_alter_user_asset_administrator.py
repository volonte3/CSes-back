# Generated by Django 4.1.3 on 2023-03-30 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0003_rename_entity_super_user_super_administraor_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='asset_administrator',
            field=models.IntegerField(),
        ),
    ]
