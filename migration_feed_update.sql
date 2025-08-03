-- Migration script to update feed tables with categories and enhanced functionality

-- Create feed_categories table
CREATE TABLE IF NOT EXISTS feed_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    description TEXT,
    icon_url VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add new columns to feed_items table
ALTER TABLE feed_items 
ADD COLUMN IF NOT EXISTS content TEXT,
ADD COLUMN IF NOT EXISTS thumbnail_url VARCHAR,
ADD COLUMN IF NOT EXISTS category_id INTEGER REFERENCES feed_categories(id),
ADD COLUMN IF NOT EXISTS tags VARCHAR,
ADD COLUMN IF NOT EXISTS author VARCHAR,
ADD COLUMN IF NOT EXISTS source VARCHAR,
ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_feed_items_category_id ON feed_items(category_id);
CREATE INDEX IF NOT EXISTS idx_feed_items_is_featured ON feed_items(is_featured);
CREATE INDEX IF NOT EXISTS idx_feed_items_created_at ON feed_items(created_at);
CREATE INDEX IF NOT EXISTS idx_feed_categories_name ON feed_categories(name);

-- Insert initial categories
INSERT INTO feed_categories (name, description, icon_url) VALUES
('Fruits', 'Information about various fruits and their health benefits', 'https://example.com/icons/fruits.png'),
('Vegetables', 'Information about various vegetables and their nutritional value', 'https://example.com/icons/vegetables.png'),
('Nutrients', 'Information about essential nutrients and their health benefits', 'https://example.com/icons/nutrients.png'),
('Herbs', 'Information about medicinal herbs and their uses', 'https://example.com/icons/herbs.png'),
('Fitness', 'Fitness tips and exercise information', 'https://example.com/icons/fitness.png'),
('Mental Health', 'Mental health and wellness information', 'https://example.com/icons/mental-health.png')
ON CONFLICT (name) DO NOTHING;

-- Update existing feed items to have default values
UPDATE feed_items SET is_featured = FALSE WHERE is_featured IS NULL;
