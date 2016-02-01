# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wms', '0034_auto_20151030_1140'),
    ]

    operations = [
        migrations.CreateModel(
            name='UGridTideDataset',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('wms.ugriddataset',),
        ),
        migrations.AddField(
            model_name='dataset',
            name='update_every',
            field=models.IntegerField(help_text='Seconds between updating this dataset. Assume datasets check at the top of the hour', default=86400),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='type',
            field=models.CharField(max_length=255, choices=[('wms.ugriddataset', 'u grid dataset'), ('wms.sgriddataset', 's grid dataset'), ('wms.rgriddataset', 'r grid dataset'), ('wms.ugridtidedataset', 'u grid tide dataset')], db_index=True),
        ),
    ]
