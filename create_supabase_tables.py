import os
import sys
from supabase import create_client

def create_tables():
    # Get Supabase credentials from environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL or SUPABASE_KEY environment variables not set.")
        sys.exit(1)
    
    # Create Supabase client
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        # Create users table if it doesn't exist
        print("Creating 'user' table in Supabase if it doesn't exist...")
        
        # Using SQL query to create table
        query = """
        CREATE TABLE IF NOT EXISTS public.user (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(64) UNIQUE NOT NULL,
            name VARCHAR(100),
            email VARCHAR(120) UNIQUE,
            password VARCHAR(256) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Execute the query using Supabase's rpc function
        result = supabase.rpc('exec_sql', {'query': query}).execute()
        
        print("Tables created successfully!")
        return True
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        return False

if __name__ == "__main__":
    create_tables()