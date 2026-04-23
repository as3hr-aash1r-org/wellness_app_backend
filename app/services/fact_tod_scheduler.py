"""
Fact TOD (Tip of the Day) Scheduler Service
Advances TOD pointers daily at 11:59 PM PKT
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from datetime import datetime
import logging

from app.database.session import SessionLocal
from app.crud.fact_crud import fact_crud

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def advance_tod_pointers_job():
    """Job to advance all TOD pointers"""
    db = SessionLocal()
    try:
        logger.info("Starting TOD pointer advancement job...")
        results = fact_crud.advance_tod_pointers(db)
        
        for fact_type, result in results.items():
            if result["status"] == "advanced":
                logger.info(
                    f"✅ {fact_type}: Advanced from fact_id {result['old_fact_id']} "
                    f"to {result['new_fact_id']}"
                )
            elif result["status"] == "skipped":
                logger.info(f"⏭️  {fact_type}: {result['reason']}")
        
        logger.info("TOD pointer advancement job completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error in TOD advancement job: {str(e)}")
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    """Initialize and start the scheduler"""
    scheduler = BackgroundScheduler(timezone=timezone('Asia/Karachi'))
    
    # Schedule job to run daily at 11:59 PM PKT
    scheduler.add_job(
        advance_tod_pointers_job,
        trigger=CronTrigger(hour=23, minute=59, timezone='Asia/Karachi'),
        id='advance_tod_pointers',
        name='Advance Fact TOD Pointers',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("📅 TOD Scheduler started - will run daily at 11:59 PM PKT")
    
    return scheduler


def stop_scheduler(scheduler: BackgroundScheduler):
    """Stop the scheduler gracefully"""
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("📅 TOD Scheduler stopped")
