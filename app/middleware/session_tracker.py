"""
Middleware to track app sessions for authenticated users
"""
from datetime import date
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.database.session import SessionLocal
from app.services.level_service import LevelService


class SessionTrackerMiddleware(BaseHTTPMiddleware):
    """
    Tracks app sessions for authenticated users.
    Records one session per user per calendar day.
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Only track for authenticated requests
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.id
            
            # Track session in background (don't block response)
            db = None
            try:
                db = SessionLocal()
                level_service = LevelService(db)
                level_service.track_app_session(user_id, date.today())
                db.commit()
            except Exception as e:
                # Log error but don't fail the request
                print(f"Session tracking error for user {user_id}: {str(e)}")
                if db:
                    db.rollback()
            finally:
                if db:
                    db.close()
        
        return response
