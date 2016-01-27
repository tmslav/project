# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.TimeField(auto_now=True)),
                ('parts_searched', models.IntegerField(default=0)),
                ('parts_found', models.IntegerField(default=0)),
                ('parts_not_found', models.IntegerField(default=0)),
                ('percent_found', models.IntegerField(default=0)),
                ('link', models.TextField(default=b'none', max_length=300)),
            ],
        ),
    ]
