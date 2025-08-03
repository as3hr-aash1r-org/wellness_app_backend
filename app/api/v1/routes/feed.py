from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.schemas.feed_schema import FeedCreate, FeedOut, FeedCategoryCreate, FeedCategoryOut
from app.schemas.api_response import success_response, APIResponse
from app.crud.feed_crud import feed_crud, feed_category_crud

router = APIRouter(prefix="/feeds", tags=["Feeds"])

# Feed Category Routes
@router.post("/categories", response_model=APIResponse[FeedCategoryOut])
def create_feed_category(category: FeedCategoryCreate, db: Session = Depends(get_db)):
    # Check if category already exists
    existing = feed_category_crud.get_by_name(db, name=category.name)
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    created = feed_category_crud.create(db, obj_in=category)
    return success_response(created, "Feed category created successfully")

@router.get("/categories", response_model=APIResponse[list[FeedCategoryOut]])
def get_all_categories(db: Session = Depends(get_db)):
    categories = feed_category_crud.get_all(db)
    return success_response(categories, "Feed categories fetched successfully")

@router.get("/categories/{category_id}", response_model=APIResponse[FeedCategoryOut])
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = feed_category_crud.get(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return success_response(category, "Category fetched successfully")

@router.put("/categories/{category_id}", response_model=APIResponse[FeedCategoryOut])
def update_category(category_id: int, category: FeedCategoryCreate, db: Session = Depends(get_db)):
    updated = feed_category_crud.update(db, category_id, category)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return success_response(updated, "Category updated successfully")

@router.delete("/categories/{category_id}", response_model=APIResponse[str])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    deleted = feed_category_crud.delete(db, category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return success_response("Category deleted", "Category deleted successfully")

# Feed Item Routes
@router.post("/", response_model=APIResponse[FeedOut])
def create_feed(feed: FeedCreate, db: Session = Depends(get_db)):
    # Validate category if provided
    if feed.category_id:
        category = feed_category_crud.get(db, feed.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    created = feed_crud.create(db, obj_in=feed)
    return success_response(created, "Feed item created successfully")

@router.get("/", response_model=APIResponse[list[FeedOut]])
def get_all_feeds(
    db: Session = Depends(get_db),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip")
):
    items = feed_crud.get_all(db, category_id=category_id, limit=limit, offset=offset)
    return success_response(items, "Feed items fetched successfully")

@router.get("/featured", response_model=APIResponse[list[FeedOut]])
def get_featured_feeds(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50, description="Number of featured items to return")
):
    items = feed_crud.get_featured(db, limit=limit)
    return success_response(items, "Featured feed items fetched successfully")

@router.get("/category/{category_id}", response_model=APIResponse[list[FeedOut]])
def get_feeds_by_category(
    category_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip")
):
    # Validate category exists
    category = feed_category_crud.get(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    items = feed_crud.get_by_category(db, category_id, limit=limit, offset=offset)
    return success_response(items, f"Feed items for category '{category.name}' fetched successfully")

@router.get("/search", response_model=APIResponse[list[FeedOut]])
def search_feeds(
    q: str = Query(..., description="Search query"),
    db: Session = Depends(get_db),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    limit: int = Query(20, ge=1, le=50, description="Number of items to return")
):
    items = feed_crud.search(db, query=q, category_id=category_id, limit=limit)
    return success_response(items, f"Search results for '{q}' fetched successfully")

@router.get("/{feed_id}", response_model=APIResponse[FeedOut])
def get_feed(feed_id: int, db: Session = Depends(get_db)):
    item = feed_crud.get(db, feed_id)
    if not item:
        raise HTTPException(status_code=404, detail="Feed item not found")
    return success_response(item, "Feed item fetched successfully")

@router.put("/{feed_id}", response_model=APIResponse[FeedOut])
def update_feed(feed_id: int, feed: FeedCreate, db: Session = Depends(get_db)):
    # Validate category if provided
    if feed.category_id:
        category = feed_category_crud.get(db, feed.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
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
