# -*- coding: utf-8 -*-
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save

from wms.tasks import update_cache, process_layers, update_dataset
from wms.models import Dataset, UGridDataset, SGridDataset, RGridDataset, UGridTideDataset
from sciwms.utils import add_periodic_task, remove_periodic_task


def schedule_dataset_update(sender, instance, created, **kwargs):
    if settings.TESTING is not True:
        if not instance.has_cache():
            update_dataset.delay(instance.pk)
        else:
            process_layers.delay(instance.pk)

        if created is True:
            add_periodic_task(name="Dataset Update: {0} ({1})".format(instance.name, instance.pk),
                              interval=instance.update_every,
                              args=[instance.pk],
                              task='wms.tasks.update_dataset')


def update_every_changed(sender, instance, **kwargs):
    try:
        obj = Dataset.objects.get(pk=instance.pk)
    except Dataset.DoesNotExist:
        pass
    else:
        if obj.update_every != instance.update_every:
            remove_periodic_task(args=[instance.pk], task='wms.tasks.update_dataset')
            add_periodic_task(name="Dataset Update: {0} ({1})".format(instance.name, instance.pk),
                              interval=instance.update_every,
                              args=[instance.pk],
                              task='wms.tasks.update_dataset')


@receiver(post_save, sender=UGridTideDataset)
def ugrid_tides_dataset_post_save(*args, **kwargs):
    schedule_dataset_update(*args, **kwargs)


@receiver(post_save, sender=UGridDataset)
def ugrid_dataset_post_save(*args, **kwargs):
    schedule_dataset_update(*args, **kwargs)


@receiver(post_save, sender=SGridDataset)
def sgrid_dataset_post_save(*args, **kwargs):
    schedule_dataset_update(*args, **kwargs)


@receiver(post_save, sender=RGridDataset)
def rgrid_dataset_post_save(*args, **kwargs):
    schedule_dataset_update(*args, **kwargs)


@receiver(post_delete, sender=UGridTideDataset)
def ugrid_tide_dataset_post_delete(sender, instance, **kwargs):
    instance.clear_cache()


@receiver(post_delete, sender=UGridDataset)
def ugrid_dataset_post_delete(sender, instance, **kwargs):
    instance.clear_cache()


@receiver(post_delete, sender=SGridDataset)
def sgrid_dataset_post_delete(sender, instance, **kwargs):
    instance.clear_cache()


@receiver(post_delete, sender=RGridDataset)
def rgrid_dataset_post_delete(sender, instance, **kwargs):
    instance.clear_cache()


@receiver(pre_save, sender=UGridTideDataset)
def ugrid_tide_dataset_pre_save(*args, **kwargs):
    update_every_changed(*args, **kwargs)


@receiver(pre_save, sender=UGridDataset)
def ugrid_dataset_pre_save(*args, **kwargs):
    update_every_changed(*args, **kwargs)


@receiver(pre_save, sender=SGridDataset)
def sgrid_dataset_pre_save(*args, **kwargs):
    update_every_changed(*args, **kwargs)


@receiver(pre_save, sender=RGridDataset)
def rgrid_dataset_pre_save(*args, **kwargs):
    update_every_changed(*args, **kwargs)
