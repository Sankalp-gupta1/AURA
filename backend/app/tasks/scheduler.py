import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.user import User
from app.services.sync_service import sync_user_data

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _auto_sync_all_users():
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.refresh_token != "").all()
        for user in users:
            try:
                sync_user_data(db, user)
                logger.info("Auto-synced user %s", user.email)
            except Exception:
                logger.exception("Auto-sync failed for user %s", user.email)
    finally:
        db.close()


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            _auto_sync_all_users,
            "interval",
            minutes=settings.AUTO_SYNC_INTERVAL_MINUTES,
            id="auto_sync_all_users",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("Background auto-sync scheduler started (every %s min)", settings.AUTO_SYNC_INTERVAL_MINUTES)


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
