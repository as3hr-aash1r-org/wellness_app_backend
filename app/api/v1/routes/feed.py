from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.feed_schema import FeedCreate, FeedOut
from app.schemas.api_response import success_response, APIResponse
from app.crud.feed_crud import feed_crud

router = APIRouter(prefix="/feeds", tags=["Feeds"])

@router.post("/", response_model=APIResponse[FeedOut])
def create_feed(feed: FeedCreate, db: Session = Depends(get_db)):
    created = feed_crud.create(db, obj_in=feed)
    return success_response(created, "Feed item created successfully")

@router.get("/", response_model=APIResponse[list[FeedOut]])
def get_all_feed(db: Session = Depends(get_db)):
    items = feed_crud.get_all(db)
    return success_response(items, "Feed items fetched successfully")

@router.get("/{feed_id}", response_model=APIResponse[FeedOut])
def get_feed(feed_id: int, db: Session = Depends(get_db)):
    item = feed_crud.get(db, feed_id)
    if not item:
        raise HTTPException(status_code=404, detail="Feed item not found")
    return success_response(item, "Feed item fetched successfully")

@router.put("/{feed_id}", response_model=APIResponse[FeedOut])
def update_feed(feed_id: int, feed: FeedCreate, db: Session = Depends(get_db)):
    updated = feed_crud.update(db, feed_id, feed)
    if not updated:
        raise HTTPException(status_code=404, detail="Feed item not found")
    return success_response(updated, "Feed item updated successfully")

@router.delete("/{feed_id}", response_model=APIResponse[str])
def delete_feed(feed_id: int, db: Session = Depends(get_db)):
    deleted = feed_crud.delete(db, feed_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Feed item not found")
    return success_response("Feed item deleted", "Feed item deleted successfully")
