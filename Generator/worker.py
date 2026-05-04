from celeryQueue import celery_app # noqa: F401
import tasks  # noqa: F401 - this line registers GENERATE_S and GENERATE_W with Celery
from celery.signals import worker_init
from model.model import model_manager

@worker_init.connect
def load_model(sender, **kwargs):
    model_manager.load()