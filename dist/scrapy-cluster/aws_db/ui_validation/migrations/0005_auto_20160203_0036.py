# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-03 00:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ui_validation', '0004_detailmodel_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detailmodel',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]