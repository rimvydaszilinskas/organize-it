# Generated by Django 3.0.14 on 2021-05-05 16:13

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CalendarEvent',
            fields=[
                ('id', models.AutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True,
                 default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('time_start', models.DateTimeField()),
                ('time_end', models.DateTimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CalendarEventAttendee',
            fields=[
                ('id', models.AutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True,
                 default=uuid.uuid4, editable=False, unique=True)),
                ('email', models.EmailField(max_length=254)),
                ('response', models.CharField(choices=[
                 ('y', 'Yes'), ('n', 'No'), ('m', 'Maybe'), ('u', 'undefined')], default='u', max_length=1)),
                ('note', models.TextField(blank=True, null=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                 related_name='attendees', to='calendars.CalendarEvent')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
