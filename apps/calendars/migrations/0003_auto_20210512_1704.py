# Generated by Django 3.2 on 2021-05-12 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendars', '0002_auto_20210505_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='calendarevent',
            name='ics_uid_override',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='calendarevent',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='calendareventattendee',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
