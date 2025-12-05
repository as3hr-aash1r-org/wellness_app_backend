# Public Challenge API Implementation

## Overview
Modified the `/challenges/type/{challenge_type}` endpoint to be a public API that works for both guest users and authenticated users, providing different levels of data based on authentication status.

## Changes Made

### 1. Added Optional Authentication Dependency (`app/dependencies/auth_dependency.py`)

**New Function:**
```python
def get_current_user_optional(
    db: Session = Depends(get_db), 
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_oauth2_scheme)
) -> Optional[User]:
    """
    Optional authentication - returns User if valid token provided, None if no token or invalid token
    Used for public endpoints that can work with or without authentication
    """
```

**Key Features:**
- Returns `User` object if valid token is provided
- Returns `None` if no token or invalid token (no exception thrown)
- Uses `HTTPBearer(auto_error=False)` for optional token extraction
- Graceful error handling without raising exceptions

### 2. Updated Challenge Endpoint (`app/api/v1/routes/challenge.py`)

**Before:**
```python
def get_challenges_by_type(
    challenge_type: ChallengeType,
    current_user: User = Depends(get_current_user)  # Required authentication
):
```

**After:**
```python
def get_challenges_by_type(
    challenge_type: ChallengeType,
    current_user: Optional[User] = Depends(get_current_user_optional)  # Optional authentication
):
```

**Key Changes:**
- **Public Access**: No authentication required
- **Conditional User Data**: User progress only included if authenticated
- **Guest Support**: Works for unauthenticated users
- **Backward Compatible**: Existing authenticated behavior preserved

## API Behavior

### For Guest Users (No Authentication)
**Request:**
```bash
GET /api/v1/challenges/type/daily
# No Authorization header
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "title": "Daily Water Challenge",
      "description": "Drink 8 glasses of water daily",
      "type": "daily",
      "duration": 7,
      "duration_type": "day",
      "reward_time": 30,
      "reward_time_type": "day",
      "is_active": true,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z",
      "duration_display_text": "7 days",
      "reward_display_text": "30 days reward",
      
      // Default user progress (guest user)
      "user_challenge_id": null,
      "status": "pending",
      "current_progress": 0,
      "progress_percentage": 0.0,
      "progress_display_text": "0/7 days",
      "remaining_actions": 7,
      "started_at": null,
      "completed_at": null,
      "last_progress_date": null,
      "last_progress_hour": null,
      "is_completed": false,
      "is_user_active": false,
      "is_authenticated": false  // Indicates guest user
    }
  ],
  "status_code": 200,
  "success": true,
  "message": "Daily challenges retrieved successfully",
  "total_pages": 1
}
```

### For Authenticated Users
**Request:**
```bash
GET /api/v1/challenges/type/daily
Authorization: Bearer <valid_token>
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "title": "Daily Water Challenge",
      "description": "Drink 8 glasses of water daily",
      "type": "daily",
      "duration": 7,
      "duration_type": "day",
      "reward_time": 30,
      "reward_time_type": "day",
      "is_active": true,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z",
      "duration_display_text": "7 days",
      "reward_display_text": "30 days reward",
      
      // Actual user progress (authenticated user)
      "user_challenge_id": 123,
      "status": "active",
      "current_progress": 3,
      "progress_percentage": 42.8,
      "progress_display_text": "3/7 days completed",
      "remaining_actions": 4,
      "started_at": "2024-01-01T10:00:00Z",
      "completed_at": null,
      "last_progress_date": "2024-01-03T15:30:00Z",
      "last_progress_hour": 15,
      "is_completed": false,
      "is_user_active": true,
      "is_authenticated": true  // Indicates authenticated user
    }
  ],
  "status_code": 200,
  "success": true,
  "message": "Daily challenges retrieved successfully",
  "total_pages": 1
}
```

## Data Differences

### Guest Users Get:
- ✅ **Challenge Information**: Full challenge details (title, description, duration, rewards)
- ✅ **Basic Structure**: All challenge fields populated
- ✅ **Default Progress**: Generic progress indicators (0 progress, "pending" status)
- ✅ **Public Data**: No sensitive user information
- ✅ **Authentication Flag**: `"is_authenticated": false`

### Authenticated Users Get:
- ✅ **Everything Guests Get**: Plus personal data
- ✅ **Personal Progress**: Actual user challenge participation
- ✅ **User Challenge ID**: Reference to user's challenge instance
- ✅ **Real Status**: Active, completed, paused, etc.
- ✅ **Progress Tracking**: Current progress, percentages, timestamps
- ✅ **Authentication Flag**: `"is_authenticated": true`

## Benefits

### 1. **Guest User Experience**
- Can browse challenges without registration
- See what challenges are available
- Understand challenge requirements and rewards
- Encourages registration to track progress

### 2. **Authenticated User Experience**
- Full personal progress tracking
- Same API endpoint for consistency
- Rich progress information
- Seamless experience

### 3. **Frontend Flexibility**
- Single API endpoint for both user types
- Conditional UI based on `is_authenticated` flag
- Easy to handle guest vs authenticated states
- Consistent data structure

### 4. **Security**
- No sensitive data exposed to guests
- Optional authentication doesn't break security
- User data only available to authenticated users
- Graceful handling of invalid tokens

## Frontend Implementation Guide

### Handling Different User States:
```javascript
// Frontend can check authentication status
const response = await fetch('/api/v1/challenges/type/daily', {
  headers: token ? { 'Authorization': `Bearer ${token}` } : {}
});

const data = await response.json();

data.data.forEach(challenge => {
  if (challenge.is_authenticated) {
    // Show user's actual progress
    showUserProgress(challenge);
  } else {
    // Show generic challenge info with "Sign up to track progress" CTA
    showGuestView(challenge);
  }
});
```

### UI Considerations:
- **Guest View**: Show challenge details + "Sign up to track progress" button
- **Authenticated View**: Show full progress tracking and interaction buttons
- **Consistent Layout**: Same challenge cards, different content based on auth status

## Error Handling

### Invalid Token:
- **Behavior**: Treats as guest user (no exception thrown)
- **Response**: Same as unauthenticated request
- **User Experience**: Seamless fallback to guest mode

### No Token:
- **Behavior**: Normal guest user flow
- **Response**: Challenge data with default progress values
- **User Experience**: Full challenge browsing capability

## Migration Impact

### Backward Compatibility:
- ✅ **Existing Apps**: Continue to work with authentication
- ✅ **API Response**: Same structure, additional `is_authenticated` field
- ✅ **Authentication**: Existing auth flows unchanged
- ✅ **User Data**: Same personal progress information

### New Capabilities:
- ✅ **Public Access**: Guest users can browse challenges
- ✅ **Marketing**: Showcase challenges to potential users
- ✅ **User Acquisition**: Encourage registration through challenge preview
- ✅ **SEO**: Public challenge data for search engines

The endpoint now serves as both a public marketing tool and a personalized user experience, adapting its response based on authentication status while maintaining full backward compatibility.