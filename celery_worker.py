from app import app
from app.tasks import celery

# Explicitly set Redis as broker and backend
celery.conf.broker_url = 'redis://localhost:6379/1'
celery.conf.result_backend = 'redis://localhost:6379/1'