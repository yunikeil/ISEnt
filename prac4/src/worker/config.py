from celery import Celery


celery = Celery(__name__)
celery.conf.broker_url = "redis://celery-broker-authprac"
celery.conf.result_backend = "redis://celery-broker-authprac"
celery.autodiscover_tasks(["worker.tasks.send_user_verify_message"])
