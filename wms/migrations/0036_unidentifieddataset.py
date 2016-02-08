# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import wms.models.datasets.base


class Migration(migrations.Migration):

    dependencies = [
        ('wms', '0035_auto_20160201_1912'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnidentifiedDataset',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('uri', models.CharField(max_length=1000)),
                ('name', models.CharField(max_length=200, help_text="Name/ID to use. No special characters or spaces ('_','0123456789' and A-Z are allowed).", unique=True)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, slugify=wms.models.datasets.base.only_underscores, populate_from='name')),
                ('job_id', models.TextField()),
            ],
        ),
    ]
