import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
database_url = os.getenv('DATABASE_URL')

# Parse the database URL
# Format: postgresql://username:password@host:port/dbname
db_parts = database_url.replace('postgresql://', '').split('@')
user_pass = db_parts[0].split(':')
host_db = db_parts[1].split('/')

username = user_pass[0]
password = user_pass[1] if len(user_pass) > 1 else ''
host_port = host_db[0].split(':')
host = host_port[0]
port = host_port[1] if len(host_port) > 1 else '5432'
dbname = host_db[1]

# Connect to the database
conn = psycopg2.connect(
    dbname=dbname,
    user=username,
    password=password,
    host=host,
    port=port
)

try:
    # Create a cursor
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Get all users with NULL emails
        cur.execute("SELECT id FROM users WHERE email IS NULL")
        null_email_users = cur.fetchall()
        
        print(f"Found {len(null_email_users)} users with NULL emails")
        
        # Update each user with a unique email
        for user in null_email_users:
            unique_email = f"user_{user['id']}@placeholder.com"
            cur.execute(
                "UPDATE users SET email = %s WHERE id = %s",
                (unique_email, user['id'])
            )
            print(f"Updated user {user['id']} with email {unique_email}")
        
        # Commit the changes
        conn.commit()
        print("All NULL emails have been updated with unique values")
        
        # Now you can run your migration to set email to NOT NULL
        print("\nNow you can run: alembic upgrade head")
        
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    conn.close()
