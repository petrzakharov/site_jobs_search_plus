# Generated by Django 4.0.4 on 2022-05-02 17:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_alter_application_written_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='written_phone',
            field=models.CharField(max_length=15, null=True, validators=[django.core.validators.RegexValidator('^\\+?1?\\d{9,15}$')]),
        ),
    ]
