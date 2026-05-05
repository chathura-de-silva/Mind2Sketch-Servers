from celeryQueue import celery_app  # noqa: F401
import tasks  # noqa: F401
from celery.signals import worker_ready
from model import model_manager


@worker_ready.connect
def load_model(sender, **kwargs):
    model_manager.load()