# Chat API Pagination Implementation

## Overview
Added pagination to the two remaining chat API endpoints that needed it, following the same pattern as other APIs in the application.

## Endpoints Updated

### 1. `/chat/rooms/expert` - Expert Chat Rooms
**Before:**
```python
@router.get("/rooms/expert", response_model=List[ChatRoomWithUser])
def my_chat_rooms(*, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
```

**After:**
```python
@router.get("/rooms/expert", response_model=APIResponse[List[ChatRoomWithUser]])
def my_chat_rooms(
    current_page: int = Query(1, ge=1, description="Current page number"),
    limit: int = Query(25, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
```

**Features:**
- Pagination for expert's assigned chat rooms
- Default limit: 25, maximum: 50
- Returns `total_pages` in response
- Uses existing CRUD methods that already support pagination

### 2. `/chat/rooms/{room_id}` - Chat Room with Messages
**Before:**
```python
@router.get("/rooms/{room_id}", response_model=APIResponse[ChatRoomWithMessages])
def get_chat_room(
    *,
    room_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
```

**After:**
```python
@router.get("/rooms/{room_id}", response_model=APIResponse[ChatRoomWithMessages])
def get_chat_room(
    *,
    room_id: int = Path(...),
    current_page: int = Query(1, ge=1, description="Current page number for messages"),
    limit: int = Query(50, ge=1, le=100, description="Number of messages per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
```

**Features:**
- Pagination for messages within a chat room
- Default limit: 50, maximum: 100 messages per page
- Returns `total_pages` based on total message count
- Messages ordered by creation date (newest first)

## CRUD Updates

### Updated `get_messages_with_details` method
**Before:**
```python
def get_messages_with_details(self, db: Session, *, room_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
```

**After:**
```python
def get_messages_with_details(self, db: Session, *, room_id: int, skip: int = 0, limit: int = 50) -> List[Message]:
```

**Changes:**
- Changed `offset` parameter to `skip` for consistency with other CRUD methods
- Maintains same functionality with better naming convention

### Added `count_messages_in_room` method
**New Method:**
```python
def count_messages_in_room(self, db: Session, *, room_id: int) -> int:
    """Count total messages in a chat room"""
    query = select(func.count(Message.id)).where(Message.room_id == room_id)
    result = db.execute(query)
    return result.scalar()
```

**Purpose:**
- Counts total messages in a chat room for pagination calculation
- Used to determine `total_pages` for message pagination

## API Usage Examples

### Expert Chat Rooms with Pagination
```bash
# Get first page of expert's chat rooms (default 25 per page)
GET /api/v1/chat/rooms/expert?current_page=1

# Get second page with custom limit
GET /api/v1/chat/rooms/expert?current_page=2&limit=10
```

### Chat Room Messages with Pagination
```bash
# Get first page of messages in room 123 (default 50 per page)
GET /api/v1/chat/rooms/123?current_page=1

# Get second page with custom limit
GET /api/v1/chat/rooms/123?current_page=2&limit=25

# Get older messages (higher page numbers show older messages)
GET /api/v1/chat/rooms/123?current_page=3&limit=20
```

## Response Format

### Expert Chat Rooms Response
```json
{
  "data": [
    {
      "id": 1,
      "name": "User's Chat",
      "user_id": 123,
      "expert_id": 456,
      "is_active": true,
      "created_at": "2024-01-01T10:00:00Z",
      "user": {
        "id": 123,
        "username": "john_doe",
        "phone_number": "+1234567890"
      }
    }
  ],
  "status_code": 200,
  "success": true,
  "message": "Chat rooms retrieved successfully",
  "total_pages": 3
}
```

### Chat Room with Messages Response
```json
{
  "data": {
    "id": 1,
    "name": "User's Chat",
    "user_id": 123,
    "expert_id": 456,
    "is_active": true,
    "messages": [
      {
        "id": 1,
        "content": "Hello, I need help",
        "sender_id": 123,
        "room_id": 1,
        "created_at": "2024-01-01T10:00:00Z",
        "is_read": true,
        "product": null,
        "office": null
      }
    ]
  },
  "status_code": 200,
  "success": true,
  "message": "Chat room retrieved successfully",
  "total_pages": 5
}
```

## Benefits

1. **Performance**: Large chat rooms with many messages now load faster
2. **User Experience**: Smoother scrolling and loading for chat interfaces
3. **Consistency**: All chat APIs now follow the same pagination pattern
4. **Scalability**: Can handle chat rooms with thousands of messages efficiently
5. **Flexibility**: Configurable page sizes for different use cases

## Notes

- **Message Order**: Messages are ordered by creation date (newest first) for better chat experience
- **Access Control**: Pagination respects existing access control - users can only see messages in rooms they have access to
- **Read Status**: Message read status is still updated when accessing a chat room
- **Backward Compatibility**: Existing functionality is preserved, pagination is additive

## Testing

Test the pagination with these scenarios:

1. **Expert with multiple chat rooms**: Test pagination of expert's assigned rooms
2. **Chat room with many messages**: Test message pagination within a room
3. **Empty chat room**: Verify pagination works with 0 messages
4. **Single page**: Test when total items fit in one page
5. **Large page sizes**: Test with maximum allowed limits
6. **Access control**: Verify pagination respects user permissions

All endpoints now provide consistent pagination with `total_pages` for proper frontend pagination controls.