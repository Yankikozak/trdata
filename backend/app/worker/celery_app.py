from celery import Celery

from app.core.config import get_settings

celery_app = Celery("tr_analytix", broker=get_settings().redis_url, backend=get_settings().redis_url)
celery_app.conf.beat_schedule = {
    "refresh-daily-risk-metrics": {
        "task": "app.worker.tasks.refresh_risk_metrics",
        "schedule": 86400.0,
    }
}
