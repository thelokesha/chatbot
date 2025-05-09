import os
import sys
import logging
import psycopg2
from psycopg2 import sql

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_supabase_connection():
    """Test the connection to Supabase PostgreSQL database directly"""
    # Get DATABASE_URL from environment or use the provided one
    database_url = os.environ.get("DATABASE_URL", "postgresql://postgres:lokesh7345@db.qjlveevoebvgxfzmsbzj.supabase.co:5432/postgres")
    
    # Fix URL if it contains brackets
    if "[" in database_url and "]" in database_url:
        database_url = database_url.replace("[", "").replace("]", "")
    
    if not database_url:
        logger.error("Missing DATABASE_URL environment variable")
        sys.exit(1)
        
    try:
        # Connect directly to PostgreSQL
        logger.info("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Test if user table exists
        logger.info("Checking if user table exists...")
        cursor.execute("""
            SELECT EXISTS (
               SELECT FROM pg_tables
               WHERE schemaname = 'public' 
               AND tablename = 'user'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            logger.info("User table exists in the database.")
            
            # Get count of users
            logger.info("Counting users in the database...")
            cursor.execute("SELECT COUNT(*) FROM public.user")
            user_count = cursor.fetchone()[0]
            logger.info(f"Found {user_count} users in the database.")
            
            # Check table structure
            logger.info("Checking user table structure...")
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'user'
            """)
            columns = cursor.fetchall()
            for column in columns:
                logger.info(f"Column: {column[0]}, Type: {column[1]}")
            
            cursor.close()
            conn.close()
            logger.info("Database connection is fully functional!")
            return True
        else:
            logger.warning("User table does not exist in the database.")
            cursor.close()
            conn.close()
            return False
            
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Supabase connection...")
    result = test_supabase_connection()
    
    if result:
        print("\n✅ Supabase connection is working properly!")
        print("The mental health chatbot application is correctly configured to use Supabase for storing user data.")
    else:
        print("\n❌ There were issues with the Supabase connection.")
        print("Please check your Supabase credentials and database configuration.")