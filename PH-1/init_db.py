#!/usr/bin/env python3
"""
EXPLAINIUM PH-1 Database Initialization Script

This script initializes the database for the EXPLAINIUM document processing system.
It automatically detects available database systems and sets up the appropriate one.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db.models import Base
from app.db.session import engine, DATABASE_URL, DATABASE_TYPE, get_db_info

def check_database_connection():
    """Check if we can connect to the database"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"✅ Database connection successful ({DATABASE_TYPE.upper()})")
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
    # PostgreSQL indexes
    postgresql_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_documents_filetype ON documents(filetype);",
        "CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);",
        "CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_entities_document_id ON knowledge_entities(document_id);",
        "CREATE INDEX IF NOT EXISTS idx_entities_label ON knowledge_entities(label);",
        "CREATE INDEX IF NOT EXISTS idx_categories_document_id ON content_categories(document_id);"
    ]
    
    # SQLite indexes (slightly different syntax)
    sqlite_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_documents_filetype ON documents(filetype);",
        "CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);",
        "CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_entities_document_id ON knowledge_entities(document_id);",
        "CREATE INDEX IF NOT EXISTS idx_entities_label ON knowledge_entities(label);",
        "CREATE INDEX IF NOT EXISTS idx_categories_document_id ON content_categories(document_id);"
    ]
    
    try:
        indexes = postgresql_indexes if DATABASE_TYPE == 'postgresql' else sqlite_indexes
        
        with engine.connect() as conn:
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                except Exception as e:
                    print(f"⚠️  Warning: Could not create index: {e}")
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
            if DATABASE_TYPE == 'postgresql':
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
            else:  # SQLite
                result = conn.execute(text("""
                    SELECT name as table_name
                    FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
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
            
            print(f"✅ All required tables present: {len(tables)} tables")
            
            # Check if we can insert and retrieve data
            conn.execute(text("""
                INSERT INTO documents (filename, filetype, status, content) 
                VALUES ('test.txt', 'txt', 'test', 'test content')
            """))
            
            result = conn.execute(text("""
                SELECT id FROM documents WHERE filename = 'test.txt'
            """))
            test_row = result.fetchone()
            if test_row:
                test_id = test_row[0]
                conn.execute(text(f"DELETE FROM documents WHERE id = {test_id}"))
            
            conn.commit()
            
            print("✅ Database read/write operations working")
            return True
            
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def display_database_info():
    """Display information about the selected database"""
    db_info = get_db_info()
    print(f"📊 Database Information:")
    print(f"   Type: {db_info['type'].upper()}")
    print(f"   URL: {db_info['url']}")
    print(f"   Status: {db_info['status']}")
    
    if DATABASE_TYPE == 'sqlite':
        print("   📝 Using SQLite - No additional setup required!")
        print("   📁 Database file will be created automatically")
    else:
        print("   🐘 Using PostgreSQL - Make sure server is running")

def main():
    """Main initialization function"""
    print("🚀 EXPLAINIUM PH-1 Database Initialization")
    print("=" * 50)
    
    display_database_info()
    print()
    
    # Step 1: Check database connection
    if not check_database_connection():
        if DATABASE_TYPE == 'postgresql':
            print("\n💡 PostgreSQL Troubleshooting tips:")
            print("1. Install PostgreSQL: brew install postgresql (macOS)")
            print("2. Start PostgreSQL: brew services start postgresql")
            print("3. Create database: createdb docdb")
            print("4. Or set DB_TYPE=sqlite to use SQLite instead")
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
    print(f"🔗 Using {DATABASE_TYPE.upper()} database")
    print("\nNext steps:")
    print("1. Start the application: uvicorn app.main:app --reload")
    print("2. Access the web interface: http://localhost:8000")
    print("3. View API documentation: http://localhost:8000/docs")
    
    if DATABASE_TYPE == 'sqlite':
        print("\n📝 Note: Using SQLite database for easy setup.")
        print("   To use PostgreSQL instead, install it and set DB_TYPE=postgresql")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
