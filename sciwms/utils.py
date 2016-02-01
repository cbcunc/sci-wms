#!python
# coding=utf-8
from __future__ import absolute_import
from functools import wraps
from datetime import timedelta

from django.core.cache import cache
from celery.schedules import schedule
from djcelery.models import PeriodicTask, IntervalSchedule
from djcelery.schedulers import ModelEntry

from sciwms import logger, celery_app


def single_job_instance(timeout):
    def task_exc(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            lock_id = 'single_job_instance-lock-{0}'.format(func.__name__)
            acquire_lock = lambda: cache.add(lock_id, 'true', timeout)
            release_lock = lambda: cache.delete(lock_id)
            if acquire_lock():
                try:
                    return func(*args, **kwargs)
                finally:
                    release_lock()
            else:
                logger.warning('{0} is already being run by another worker. Skipping.'.format(func.__name__))
        return wrapper
    return task_exc


def bound_pk_lock(timeout):
    def task_exc(func):
        @wraps(func)
        def wrapper(f, *args, **kwargs):
            pk = args[0]
            lock_id = '{0}-lock-{1}'.format(f.__name__, pk)
            acquire_lock = lambda: cache.add(lock_id, 'true', timeout)
            release_lock = lambda: cache.delete(lock_id)
            if acquire_lock():
                try:
                    return func(f, *args, **kwargs)
                finally:
                    release_lock()
            else:
                logger.warning('{0} with pk {1} is already being run by another worker. Skipping.'.format(func.__name__, pk))
        return wrapper
    return task_exc


def pk_lock(timeout):
    def task_exc(func):
        @wraps(func)
        def wrapper(pk, *args, **kwargs):
            lock_id = '{0}-lock-{1}'.format(func.__name__, pk)
            acquire_lock = lambda: cache.add(lock_id, 'true', timeout)
            release_lock = lambda: cache.delete(lock_id)
            if acquire_lock():
                try:
                    return func(pk, *args, **kwargs)
                finally:
                    release_lock()
            else:
                logger.warning('{0} with pk {1} is already being run by another worker. Skipping.'.format(func.__name__, pk))
        return wrapper
    return task_exc


def schedule_task(task, *args, **kwargs):
    inspect = celery_app.control.inspect()
    try:
        for k, v in inspect.scheduled().iteritems():
            for t in v:
                if t['request']['name'] == task.name and list(*args) == t['request']['args']:
                    return
    except BaseException:
        # No workers are running.  Either TESTING or didn't start any...
        pass
    task.apply_async(*args, **kwargs)


def add_periodic_task(name, task, interval, args):
    intervalSchedule = IntervalSchedule.from_schedule(schedule(timedelta(seconds=interval)))
    intervalSchedule.save()

    args = stringify_list(args)

    modelData = dict(
        name=name,
        task=task,
        interval_id=intervalSchedule.pk,
        args=args
    )

    periodicTask = PeriodicTask(**modelData)
    periodicTask.save()

    me = ModelEntry(periodicTask)
    me.save()


def remove_periodic_task(task, args):
    args = stringify_list(args)
    for pt in PeriodicTask.objects.all().filter(task=task, args=args):
        pt.delete()


def update_periodic_task(task, oldargs, newargs):
    oldargs = stringify_list(oldargs)
    newargs = stringify_list(newargs)
    for pt in PeriodicTask.objects.all().filter(task=task, args=oldargs):
        pt.args = newargs
        pt.save()


def get_periodic_task(task, args):
    args = stringify_list(args)
    try:
        return PeriodicTask.objects.get(task=task, args=args)
    except PeriodicTask.DoesNotExist:
        return None


def stringify_list(thing):
    if isinstance(thing, (list, tuple)):
        return str(thing)
    return thing
