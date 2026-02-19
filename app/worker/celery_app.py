
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"]
)

# Configure Celery Beat Schedule
celery_app.conf.beat_schedule = {
    "monitor-strategies-every-minute": {
        "task": "app.worker.tasks.run_strategy_monitor",
        "schedule": crontab(minute="*"), # Run every minute
    },
}

celery_app.conf.timezone = "Asia/Shanghai"
