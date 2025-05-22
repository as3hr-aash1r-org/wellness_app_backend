-- First update existing records to have a type
UPDATE messages SET type = 'text' WHERE type IS NULL;

-- Add media fields
ALTER TABLE messages ADD COLUMN media_url VARCHAR;
ALTER TABLE messages ADD COLUMN media_duration INTEGER;
ALTER TABLE messages ADD COLUMN media_size INTEGER;
ALTER TABLE messages ADD COLUMN media_name VARCHAR;
ALTER TABLE messages ADD COLUMN updated_at TIMESTAMP;

-- Now make type NOT NULL
ALTER TABLE messages ALTER COLUMN type SET NOT NULL;
