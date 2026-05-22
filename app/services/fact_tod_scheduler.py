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
from app.models.user import User
from app.services.firebase_service import firebase_notification_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_fact_notification_to_all_users(db):
    """Send fact of the day notification to all users with FCM tokens"""
    try:
        # Get all users with FCM tokens
        users = db.query(User).filter(User.fcm_token.isnot(None)).all()
        
        if not users:
            logger.info("No users with FCM tokens found")
            return
        
        title = "Fact of the Day"
        body = "Check out today's health facts and boost your wellness knowledge!"
        
        success_count = 0
        failed_count = 0
        
        for user in users:
            try:
                firebase_notification_service.send_notification(
                    token=user.fcm_token,
                    title=title,
                    body=body,
                    data={
                        "type": "fact_of_the_day",
                        "title": title,
                        "body": body
                    }
                )
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to send notification to user {user.id}: {str(e)}")
                failed_count += 1
        
        logger.info(f"📱 Sent fact notifications: {success_count} successful, {failed_count} failed")
        
    except Exception as e:
        logger.error(f"Error sending fact notifications: {str(e)}")


def advance_tod_pointers_job():
    """Job to advance all TOD pointers and send notifications"""
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
        
        # Send notification to all users
        send_fact_notification_to_all_users(db)
        
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
