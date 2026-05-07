from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException

from app.models.support_ticket import SupportTicket, TicketStatus
from app.schemas.support_ticket_schema import SupportTicketCreate


class CRUDSupportTicket:
    def create(
        self, 
        db: Session, 
        *, 
        obj_in: SupportTicketCreate, 
        user_id: int
    ) -> SupportTicket:
        """Create a new support ticket"""
        ticket = SupportTicket(
            user_id=user_id,
            subject=obj_in.subject,
            description=obj_in.description,
            file_url=obj_in.file_url,
            status=TicketStatus.pending
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket
    
    def get_by_id(self, db: Session, *, ticket_id: int) -> Optional[SupportTicket]:
        """Get ticket by ID"""
        query = select(SupportTicket).where(SupportTicket.id == ticket_id)
        result = db.execute(query)
        return result.scalar_one_or_none()
    
    def get_user_tickets(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        status: Optional[TicketStatus] = None
    ) -> List[SupportTicket]:
        """Get all tickets for a specific user, optionally filtered by status"""
        query = select(SupportTicket).where(SupportTicket.user_id == user_id)
        
        if status:
            query = query.where(SupportTicket.status == status)
        
        query = query.order_by(SupportTicket.created_at.desc())
        result = db.execute(query)
        return list(result.scalars().all())
    
    def get_all_tickets(
        self, 
        db: Session, 
        *, 
        status: Optional[TicketStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[SupportTicket]:
        """Get all tickets across all users (admin), optionally filtered by status"""
        query = select(SupportTicket)
        
        if status:
            query = query.where(SupportTicket.status == status)
        
        query = query.order_by(SupportTicket.created_at.desc()).offset(skip).limit(limit)
        result = db.execute(query)
        return list(result.scalars().all())
    
    def reply_to_ticket(
        self, 
        db: Session, 
        *, 
        ticket_id: int, 
        admin_reply: str
    ) -> SupportTicket:
        """Admin replies to a ticket and marks it as answered"""
        ticket = self.get_by_id(db, ticket_id=ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        ticket.admin_reply = admin_reply
        ticket.status = TicketStatus.answered
        ticket.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(ticket)
        return ticket


support_ticket_crud = CRUDSupportTicket()
