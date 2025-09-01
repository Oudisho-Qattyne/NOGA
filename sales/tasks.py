
from celery import shared_task
from .utils.association_rules import update_association_rules

@shared_task
def update_rules_task():
    """مهمة خلفية لتحديث قواعد الارتباط."""
    return update_association_rules()
