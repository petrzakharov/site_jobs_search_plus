# Generated by Django 4.0.4 on 2022-05-05 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_alter_application_written_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resume',
            name='experience',
            field=models.TextField(max_length=1000),
        ),
    ]