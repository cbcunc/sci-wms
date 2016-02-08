# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wms', '0038_auto_20160208_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='update_task',
            field=models.CharField(max_length=200, blank=True, help_text='The Celery task_id when this dataset is updating. Used for progress and front-end stuff.'),
        ),
    ]
