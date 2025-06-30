#!/usr/bin/env python3
"""
EXPLAINIUM PH-1 Database Initialization Script

This script initializes the PostgreSQL database for the EXPLAINIUM
document processing system.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db.models import Base
from app.db.session import DATABASE_URL, engine

def check_database_connection():
    """Check if we can connect to the database"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        return True
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def create_indexes():
    """Create database indexes for better performance"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_documents_filetype ON documents(filetype);",
        "CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);",
        "CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);"
    ]
    
    try:
        with engine.connect() as conn:
            for index_sql in indexes:
                conn.execute(text(index_sql))
            conn.commit()
        print("✅ Database indexes created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create indexes: {e}")
        return False

def verify_setup():
    """Verify the database setup"""
    try:
        with engine.connect() as conn:
            # Check if tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            
            expected_tables = [
                'documents', 'knowledge_entities', 'knowledge_relationships',
                'content_categories', 'key_phrases', 'document_structures',
                'video_frames'
            ]
            missing_tables = [t for t in expected_tables if t not in tables]
            
            if missing_tables:
                print(f"❌ Missing tables: {missing_tables}")
                return False
            
            print(f"✅ All required tables present: {tables}")
            
            # Check if we can insert and retrieve data
            conn.execute(text("""
                INSERT INTO documents (filename, filetype, status, content) 
                VALUES ('test.txt', 'txt', 'test', 'test content')
            """))
            
            result = conn.execute(text("""
                SELECT id FROM documents WHERE filename = 'test.txt'
            """))
            test_id = result.fetchone()[0]
            
            conn.execute(text(f"DELETE FROM documents WHERE id = {test_id}"))
            conn.commit()
            
            print("✅ Database read/write operations working")
            return True
            
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def main():
    """Main initialization function"""
    print("🚀 EXPLAINIUM PH-1 Database Initialization")
    print("=" * 50)
    
    print(f"Database URL: {DATABASE_URL}")
    print()
    
    # Step 1: Check database connection
    if not check_database_connection():
        print("\n💡 Troubleshooting tips:")
        print("1. Ensure PostgreSQL is running")
        print("2. Check database credentials in environment variables")
        print("3. Verify database exists: createdb docdb")
        return False
    
    # Step 2: Create tables
    if not create_tables():
        return False
    
    # Step 3: Create indexes
    if not create_indexes():
        return False
    
    # Step 4: Verify setup
    if not verify_setup():
        return False
    
    print("\n🎉 Database initialization completed successfully!")
    print("\nNext steps:")
    print("1. Start the application: uvicorn app.main:app --reload")
    print("2. Access the web interface: http://localhost:8000")
    print("3. View API documentation: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
