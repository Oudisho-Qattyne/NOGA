from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from .tasks import update_rules_task

@receiver(post_save, sender=Product)
def regenerate_rules_on_new_product(sender, instance, created, **kwargs):
    """
    عندما يضاف منتج جديد، نقوم بإعادة توليد القواعد بالخلفية.
    """
    if created:
        update_rules_task.delay()