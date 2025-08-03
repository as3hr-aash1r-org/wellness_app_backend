# Feed API Documentation

## Overview
The feed system now supports categorized educational content similar to the health library shown in the mobile app screenshot. Users can browse content by categories like "Fruits", "Vegetables", "Nutrients", etc.

## Feed Categories

### Get All Categories
```
GET /api/feeds/categories
```
Returns a list of all available feed categories.

**Response Example:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Fruits",
      "description": "Information about various fruits and their health benefits",
      "icon_url": "https://example.com/icons/fruits.png",
      "created_at": "2023-08-03T16:00:00Z"
    }
  ],
  "success": true,
  "message": "Feed categories fetched successfully"
}
```

### Create Category
```
POST /api/feeds/categories
```
Creates a new feed category.

**Request Body:**
```json
{
  "name": "Fruits",
  "description": "Information about various fruits and their health benefits",
  "icon_url": "https://example.com/icons/fruits.png"
}
```

### Get Category by ID
```
GET /api/feeds/categories/{category_id}
```

### Update Category
```
PUT /api/feeds/categories/{category_id}
```

### Delete Category
```
DELETE /api/feeds/categories/{category_id}
```

## Feed Items

### Get All Feeds
```
GET /api/feeds/
```
Returns all feed items with optional filtering.

**Query Parameters:**
- `category_id` (optional): Filter by category ID
- `limit` (optional, default: 50): Number of items to return
- `offset` (optional, default: 0): Number of items to skip

**Response Example:**
```json
{
  "data": [
    {
      "id": 1,
      "title": "10 Health Benefits of Apple",
      "description": "Apples are packed with nutrients and offer numerous health benefits.",
      "content": "Apple health benefits includes promoting oral health...",
      "type": "post",
      "media_url": null,
      "thumbnail_url": "https://example.com/images/apple-benefits.jpg",
      "category_id": 1,
      "tags": "apple, health, nutrition, antioxidants",
      "author": "healthline.com",
      "source": "Healthline",
      "is_featured": true,
      "created_at": "2023-08-03T16:00:00Z"
    }
  ],
  "success": true,
  "message": "Feed items fetched successfully"
}
```

### Get Featured Feeds
```
GET /api/feeds/featured
```
Returns featured feed items.

**Query Parameters:**
- `limit` (optional, default: 10): Number of featured items to return

### Get Feeds by Category
```
GET /api/feeds/category/{category_id}
```
Returns all feed items for a specific category.

**Query Parameters:**
- `limit` (optional, default: 50): Number of items to return
- `offset` (optional, default: 0): Number of items to skip

### Search Feeds
```
GET /api/feeds/search?q={search_query}
```
Search through feed items by title, description, content, and tags.

**Query Parameters:**
- `q` (required): Search query
- `category_id` (optional): Filter search results by category
- `limit` (optional, default: 20): Number of results to return

### Create Feed Item
```
POST /api/feeds/
```
Creates a new feed item.

**Request Body:**
```json
{
  "title": "10 Health Benefits of Apple",
  "description": "Apples are packed with nutrients and offer numerous health benefits.",
  "content": "Detailed content about apple health benefits...",
  "type": "post",
  "media_url": null,
  "thumbnail_url": "https://example.com/images/apple-benefits.jpg",
  "category_id": 1,
  "tags": "apple, health, nutrition, antioxidants",
  "author": "healthline.com",
  "source": "Healthline",
  "is_featured": true
}
```

### Get Feed Item by ID
```
GET /api/feeds/{feed_id}
```

### Update Feed Item
```
PUT /api/feeds/{feed_id}
```

### Delete Feed Item
```
DELETE /api/feeds/{feed_id}
```

## Data Models

### FeedCategory
- `id`: Integer (Primary Key)
- `name`: String (Unique, Required)
- `description`: String (Optional)
- `icon_url`: String (Optional)
- `created_at`: DateTime

### FeedItem
- `id`: Integer (Primary Key)
- `title`: String (Required)
- `description`: String (Optional)
- `content`: String (Optional) - Full content for detailed posts
- `type`: Enum (post, video, reel)
- `media_url`: String (Optional) - URL for video/audio content
- `thumbnail_url`: String (Optional) - Thumbnail for posts/videos
- `category_id`: Integer (Foreign Key, Optional)
- `tags`: String (Optional) - Comma-separated tags
- `author`: String (Optional)
- `source`: String (Optional) - Source website/organization
- `is_featured`: Boolean (Default: False)
- `created_at`: DateTime

## Usage Examples

### Frontend Integration
1. **Display Categories**: Fetch categories and display them as horizontal scrollable tabs
2. **Category-based Feed**: When user taps on a category, fetch feeds for that category
3. **Search**: Implement search functionality across all feeds or within a category
4. **Featured Content**: Display featured content prominently on the main feed page

### Sample API Calls

#### Get categories for the horizontal menu:
```bash
curl -X GET "http://localhost:8000/api/feeds/categories"
```

#### Get feeds for "Fruits" category:
```bash
curl -X GET "http://localhost:8000/api/feeds/category/1?limit=20"
```

#### Search for apple-related content:
```bash
curl -X GET "http://localhost:8000/api/feeds/search?q=apple&limit=10"
```

#### Create a new feed item:
```bash
curl -X POST "http://localhost:8000/api/feeds/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Benefits of Oranges",
    "description": "Oranges are rich in vitamin C and other nutrients",
    "type": "post",
    "category_id": 1,
    "tags": "orange, vitamin C, citrus",
    "is_featured": false
  }'
```

## Database Setup

1. Run the migration script:
```bash
psql -d your_database -f migration_feed_update.sql
```

2. Populate initial data:
```bash
python populate_feed_data.py
```

This will create the necessary tables and populate them with sample categories and feed items similar to what's shown in the mobile app screenshot.
