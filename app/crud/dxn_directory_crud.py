from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.dxn_directory import DXNDirectory
from app.schemas.dxn_directory_schema import DXNDirectoryCreate, DXNDirectoryUpdate
from fastapi import HTTPException
from typing import Optional, List

class DXNDirectoryCRUD:
    def create(self, db: Session, obj_in: DXNDirectoryCreate) -> DXNDirectory:
        entry = DXNDirectory(**obj_in.model_dump())
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    def get(self, db: Session, entry_id: int) -> Optional[DXNDirectory]:
        return db.query(DXNDirectory).filter(DXNDirectory.id == entry_id).first()

    def update(self, db: Session, entry_id: int, obj_in: DXNDirectoryUpdate) -> Optional[DXNDirectory]:
        entry = self.get(db, entry_id)
        if not entry:
            return None
        for key, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(entry, key, value)
        db.commit()
        db.refresh(entry)
        return entry

    def delete(self, db: Session, entry_id: int):
        entry = self.get(db, entry_id)
        if entry:
            db.delete(entry)
            db.commit()
        return entry

    def search_filter_paginate(self, db: Session, search: Optional[str], filters: dict, skip: int, limit: int) -> List[DXNDirectory]:
        query = db.query(DXNDirectory)
        if search:
            search_filter = or_(
                DXNDirectory.country.ilike(f"%{search}%"),
                DXNDirectory.person.ilike(f"%{search}%"),
                DXNDirectory.position.ilike(f"%{search}%"),
                DXNDirectory.city.ilike(f"%{search}%"),
                DXNDirectory.province_state.ilike(f"%{search}%"),
                DXNDirectory.phone1.ilike(f"%{search}%"),
                DXNDirectory.phone2.ilike(f"%{search}%"),
                DXNDirectory.whatsapp1.ilike(f"%{search}%"),
                DXNDirectory.whatsapp2.ilike(f"%{search}%"),
                DXNDirectory.email1.ilike(f"%{search}%"),
                DXNDirectory.email2.ilike(f"%{search}%"),
                DXNDirectory.website.ilike(f"%{search}%"),
                DXNDirectory.address_line1.ilike(f"%{search}%"),
                DXNDirectory.address_line2.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)
        for k, v in filters.items():
            if v:
                query = query.filter(getattr(DXNDirectory, k) == v)
        return query.offset(skip).limit(limit).all()

    def count(self, db: Session, search: Optional[str], filters: dict) -> int:
        query = db.query(DXNDirectory)
        if search:
            search_filter = or_(
                DXNDirectory.country.ilike(f"%{search}%"),
                DXNDirectory.person.ilike(f"%{search}%"),
                DXNDirectory.position.ilike(f"%{search}%"),
                DXNDirectory.city.ilike(f"%{search}%"),
                DXNDirectory.province_state.ilike(f"%{search}%"),
                DXNDirectory.phone1.ilike(f"%{search}%"),
                DXNDirectory.phone2.ilike(f"%{search}%"),
                DXNDirectory.whatsapp1.ilike(f"%{search}%"),
                DXNDirectory.whatsapp2.ilike(f"%{search}%"),
                DXNDirectory.email1.ilike(f"%{search}%"),
                DXNDirectory.email2.ilike(f"%{search}%"),
                DXNDirectory.website.ilike(f"%{search}%"),
                DXNDirectory.address_line1.ilike(f"%{search}%"),
                DXNDirectory.address_line2.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)
        for k, v in filters.items():
            if v:
                query = query.filter(getattr(DXNDirectory, k) == v)
        return query.count()

dxn_directory_crud = DXNDirectoryCRUD()
