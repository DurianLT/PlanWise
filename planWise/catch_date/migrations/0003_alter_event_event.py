# Generated by Django 5.0.4 on 2024-04-19 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catch_date', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event',
            field=models.TextField(),
        ),
    ]
