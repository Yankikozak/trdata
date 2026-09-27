from app.worker.celery_app import celery_app


@celery_app.task
def refresh_risk_metrics() -> dict[str, str]:
    # Production implementation will load validated prices and persist model outputs.
    return {"status": "queued", "source": "provider-adapter-required"}
