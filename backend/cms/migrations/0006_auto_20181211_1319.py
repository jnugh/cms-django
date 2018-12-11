# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-11 13:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0005_event_startdate_enddate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='location',
        ),
        migrations.RemoveField(
            model_name='eventtranslation',
            name='event',
        ),
        migrations.RemoveField(
            model_name='eventtranslation',
            name='user',
        ),
        migrations.DeleteModel(
            name='Event',
        ),
        migrations.DeleteModel(
            name='EventTranslation',
        ),
    ]
