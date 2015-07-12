from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from models import Sighting, Notification


@receiver(post_save, weak=False, dispatch_uid="sighting_on_post_save")
def sighting_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        if isinstance(instance, Sighting):
            try:
                Notification.objects.get(sighting=instance)
            except Notification.DoesNotExist:
                Notification.objects.create(notification_datetime=datetime.now(),
                                            sighting=instance
                                            )