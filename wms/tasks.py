# -*- coding: utf-8 -*-
from __future__ import absolute_import
from collections import namedtuple

from datetime import datetime
import pytz

from celery import shared_task
from django.db.utils import IntegrityError

from wms.models.datasets.base import Dataset

from sciwms.utils import single_job_instance, bound_pk_lock, pk_lock, add_periodic_task, get_periodic_task, remove_periodic_task


@shared_task(bind=True, default_retry_delay=300)
@bound_pk_lock(timeout=1200)
def process_layers(self, pkey, **kwargs):
    try:
        d = Dataset.objects.get(pk=pkey)
        if hasattr(d, 'process_layers'):
            d.process_layers()
        return 'Processed {} ({!s})'.format(d.name, d.pk)
    except Dataset.DoesNotExist:
        return 'Dataset did not exist, can not complete task'
    except BaseException as e:
        self.retry(exc=e)


@shared_task(bind=True, default_retry_delay=300)
@bound_pk_lock(timeout=1200)
def update_cache(self, pkey, **kwargs):
    try:
        d = Dataset.objects.get(pk=pkey)
        if hasattr(d, 'update_cache'):
            d.update_cache(**kwargs)

        # Save without callbacks
        Dataset.objects.filter(pk=pkey).update(cache_last_updated=datetime.utcnow().replace(tzinfo=pytz.utc))
        return 'Updated {} ({!s})'.format(d.name, d.pk)
    except Dataset.DoesNotExist:
        return 'Dataset did not exist, can not complete task'
    except BaseException as e:
        self.retry(exc=e)


@shared_task
@single_job_instance(timeout=7200)
def update_dataset(pkey, **kwargs):
    (process_layers.si(pkey, **kwargs) | update_cache.si(pkey, **kwargs)).delay()
    return 'Scheduled dataset update'


@shared_task
@pk_lock(timeout=1200)
def add_dataset(name, uri):
    klass = Dataset.identify(uri)
    if klass is not None:
        try:
            ds = klass.objects.create(name=name, uri=uri)
            return 'Added {}'.format(ds.name)
        except IntegrityError:
            return 'Could not add dataset, name "{}" already exists'.format(name)
    else:
        return 'No dataset types found to process {}'.format(uri)


@shared_task
@single_job_instance(timeout=300)
def regulate():
    updates_scheduled = 0
    for d in Dataset.objects.all():
        if d.keep_up_to_date is True:
            # Make sure all changing datasets have an update job
            if get_periodic_task(args=[d.pk], task='wms.tasks.update_dataset') is None:
                add_periodic_task(name="Dataset Update: {0} ({1})".format(d.name, d.pk), interval=d.update_every,
                                  args=[d.pk], task='wms.tasks.update_dataset')
                updates_scheduled += 1
        else:
            # Remove periodic jobs if the folder is no longer changing
            remove_periodic_task(args=[d.pk], task='wms.tasks.update_dataset')

    results = namedtuple('Results', ['updates_scheduled'])
    return results(updates_scheduled=updates_scheduled)
