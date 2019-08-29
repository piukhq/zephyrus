from celery import Celery

from settings import CeleryConf

app = Celery()
app.config_from_object(CeleryConf, namespace='celery')
