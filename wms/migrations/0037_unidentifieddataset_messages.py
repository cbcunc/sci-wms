# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wms', '0036_unidentifieddataset'),
    ]

    operations = [
        migrations.AddField(
            model_name='unidentifieddataset',
            name='messages',
            field=models.TextField(default='None'),
            preserve_default=False,
        ),
    ]
