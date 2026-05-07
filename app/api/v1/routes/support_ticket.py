from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User, UserRole
from app.models.support_ticket import TicketStatus
from app.schemas.support_ticket_schema import (
    SupportTicketCreate,
    SupportTicketOut,
    AdminReplyRequest
)
from app.schemas.api_response import success_response, APIResponse
from app.crud.support_ticket_crud import support_ticket_crud
from app.core.decorators import standardize_response


router = APIRouter(prefix="/support", tags=["Support Tickets"])


def check_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verify user is admin"""
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ==================== User Routes ====================

@router.post("/tickets", response_model=APIResponse[SupportTicketOut])
@standardize_response
def create_ticket(
    ticket_data: SupportTicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new support ticket (User).
    Frontend uploads file to Firebase and sends URL.
    """
    ticket = support_ticket_crud.create(
        db,
        obj_in=ticket_data,
        user_id=current_user.id
    )
    
    return success_response(
        data=ticket,
        message="Support ticket created successfully",
        status_code=201
    )


@router.get("/tickets", response_model=APIResponse[List[SupportTicketOut]])
@standardize_response
def get_my_tickets(
    status: Optional[TicketStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get logged-in user's own tickets, optionally filtered by status.
    """
    tickets = support_ticket_crud.get_user_tickets(
        db,
        user_id=current_user.id,
        status=status
    )
    
    return success_response(
        data=tickets,
        message="Tickets fetched successfully"
    )


# ==================== Admin Routes ====================

@router.get("/admin/tickets", response_model=APIResponse[List[SupportTicketOut]])
@standardize_response
def get_all_tickets(
    status: Optional[TicketStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Get all support tickets across all users (Admin only).
    Optionally filtered by status.
    """
    tickets = support_ticket_crud.get_all_tickets(
        db,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        data=tickets,
        message="All tickets fetched successfully"
    )


@router.patch("/admin/tickets/{ticket_id}/reply", response_model=APIResponse[SupportTicketOut])
@standardize_response
def reply_to_ticket(
    ticket_id: int,
    reply_data: AdminReplyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """
    Admin replies to a ticket (Admin only).
    Sets admin_reply and changes status to "Answered".
    """
    ticket = support_ticket_crud.reply_to_ticket(
        db,
        ticket_id=ticket_id,
        admin_reply=reply_data.admin_reply
    )
    
    return success_response(
        data=ticket,
        message="Reply sent successfully"
    )
