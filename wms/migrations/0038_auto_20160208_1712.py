# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wms', '0037_unidentifieddataset_messages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unidentifieddataset',
            name='job_id',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='unidentifieddataset',
            name='messages',
            field=models.TextField(blank=True, null=True),
        ),
    ]
