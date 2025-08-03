#!/usr/bin/env python3
"""
Script to populate the database with initial feed categories and sample data
"""

import sys
sys.path.append('.')

from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.feed import FeedCategory, FeedItem, FeedType
from app.database.base import Base
from app.database.session import engine

# Create all tables
Base.metadata.create_all(bind=engine)

def populate_categories():
    """Populate feed categories"""
    db = SessionLocal()
    try:
        categories_data = [
            {
                "name": "Fruits",
                "description": "Information about various fruits and their health benefits",
                "icon_url": "https://example.com/icons/fruits.png"
            },
            {
                "name": "Vegetables",
                "description": "Information about various vegetables and their nutritional value",
                "icon_url": "https://example.com/icons/vegetables.png"
            },
            {
                "name": "Nutrients",
                "description": "Information about essential nutrients and their health benefits",
                "icon_url": "https://example.com/icons/nutrients.png"
            },
            {
                "name": "Herbs",
                "description": "Information about medicinal herbs and their uses",
                "icon_url": "https://example.com/icons/herbs.png"
            },
            {
                "name": "Fitness",
                "description": "Fitness tips and exercise information",
                "icon_url": "https://example.com/icons/fitness.png"
            },
            {
                "name": "Mental Health",
                "description": "Mental health and wellness information",
                "icon_url": "https://example.com/icons/mental-health.png"
            }
        ]
        
        for category_data in categories_data:
            # Check if category already exists
            existing = db.query(FeedCategory).filter_by(name=category_data["name"]).first()
            if not existing:
                category = FeedCategory(**category_data)
                db.add(category)
                print(f"Added category: {category_data['name']}")
            else:
                print(f"Category already exists: {category_data['name']}")
        
        db.commit()
        print("Categories populated successfully!")
        
    except Exception as e:
        print(f"Error populating categories: {e}")
        db.rollback()
    finally:
        db.close()

def populate_sample_feeds():
    """Populate sample feed items"""
    db = SessionLocal()
    try:
        # Get category IDs
        fruits_category = db.query(FeedCategory).filter_by(name="Fruits").first()
        vegetables_category = db.query(FeedCategory).filter_by(name="Vegetables").first()
        nutrients_category = db.query(FeedCategory).filter_by(name="Nutrients").first()
        
        if not fruits_category:
            print("Fruits category not found. Please run populate_categories first.")
            return
            
        sample_feeds = [
            {
                "title": "10 Health Benefits of Apple",
                "description": "Apples are packed with nutrients and offer numerous health benefits.",
                "content": """
                Apple health benefits includes promoting oral health, maintaining cardiovascular health, a healthy snack for diabetics, improving respiratory health, fighting cancer cells, preventing osteoporosis, helps cure night blindness, helps boost energy level, enhancing skin conditions, preventing premature aging, controlling body weight, maintaining neuroprotection systems, preventing haemorrhoids.
                
                1. Build Stronger Bones
                2. Improve Your Eyesight
                3. Fight Against Cancer
                4. Improve Brain Function
                5. Provides Antioxidant Benefits
                6. Provides Anti-Cancer Benefits
                7. Provides Anti-Asthma Benefits
                8. Strengthen Immunity
                9. Balance Blood Sugar Levels
                10. Stimulate Weight Loss
                """,
                "type": FeedType.post,
                "thumbnail_url": "https://example.com/images/apple-benefits.jpg",
                "category_id": fruits_category.id,
                "tags": "apple, health, nutrition, antioxidants",
                "author": "healthline.com",
                "source": "Healthline",
                "is_featured": True
            },
            {
                "title": "Benefits of Eating Bananas Daily",
                "description": "Discover why bananas should be part of your daily diet.",
                "content": """
                Bananas are among the world's most popular fruits. They contain essential nutrients that can have a protective impact on health.
                
                Key Benefits:
                - Rich in potassium for heart health
                - High in vitamin B6
                - Good source of vitamin C
                - Contains dietary fiber
                - Natural energy booster
                """,
                "type": FeedType.post,
                "thumbnail_url": "https://example.com/images/banana-benefits.jpg",
                "category_id": fruits_category.id,
                "tags": "banana, potassium, energy, heart health",
                "author": "nutrition.org",
                "source": "Nutrition Foundation",
                "is_featured": False
            },
            {
                "title": "Spinach: The Ultimate Superfood",
                "description": "Learn about the incredible nutritional value of spinach.",
                "content": """
                Spinach is loaded with nutrients and antioxidants, and is considered one of the healthiest foods on the planet.
                
                Nutritional Benefits:
                - High in iron and folate
                - Rich in vitamins A, C, and K
                - Contains antioxidants like lutein
                - Good source of plant-based protein
                - Supports eye health
                """,
                "type": FeedType.post,
                "thumbnail_url": "https://example.com/images/spinach-benefits.jpg",
                "category_id": vegetables_category.id if vegetables_category else None,
                "tags": "spinach, iron, vitamins, superfood",
                "author": "healthyeating.org",
                "source": "Healthy Eating Guide",
                "is_featured": True
            },
            {
                "title": "Vitamin D: The Sunshine Vitamin",
                "description": "Understanding the importance of Vitamin D for your health.",
                "content": """
                Vitamin D is crucial for bone health and immune function. It's often called the sunshine vitamin because your skin produces it in response to sunlight.
                
                Key Functions:
                - Helps calcium absorption
                - Supports immune system
                - Maintains bone health
                - May reduce depression risk
                - Supports muscle function
                """,
                "type": FeedType.post,
                "thumbnail_url": "https://example.com/images/vitamin-d.jpg",
                "category_id": nutrients_category.id if nutrients_category else None,
                "tags": "vitamin D, sunshine, bones, immunity",
                "author": "medicaltoday.com",
                "source": "Medical Today",
                "is_featured": False
            }
        ]
        
        for feed_data in sample_feeds:
            # Check if feed already exists
            existing = db.query(FeedItem).filter_by(title=feed_data["title"]).first()
            if not existing:
                feed = FeedItem(**feed_data)
                db.add(feed)
                print(f"Added feed: {feed_data['title']}")
            else:
                print(f"Feed already exists: {feed_data['title']}")
        
        db.commit()
        print("Sample feeds populated successfully!")
        
    except Exception as e:
        print(f"Error populating feeds: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Populating feed categories...")
    populate_categories()
    
    print("\nPopulating sample feed items...")
    populate_sample_feeds()
    
    print("\nDatabase population completed!")
