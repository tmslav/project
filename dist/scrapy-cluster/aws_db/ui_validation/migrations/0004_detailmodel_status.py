# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-02 23:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ui_validation', '0003_auto_20160202_1311'),
    ]

    operations = [
        migrations.AddField(
            model_name='detailmodel',
            name='status',
            field=models.CharField(default=b'pending', max_length=300),
        ),
    ]
