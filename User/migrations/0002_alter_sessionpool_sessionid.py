# Generated by Django 4.1.3 on 2023-03-28 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionpool',
            name='sessionId',
            field=models.CharField(max_length=48),
        ),
    ]
