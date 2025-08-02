#!/usr/bin/env python3

import sys
from sqlalchemy import create_engine
from database import Base

# Use sync engine for table creation
SYNC_DATABASE_URL = 'postgresql://postgres:netvexa_password@localhost:5433/netvexa_db'

def init_database():
    """Initialize database tables"""
    print("Connecting to database...")
    engine = create_engine(SYNC_DATABASE_URL)
    
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    print("✓ Database tables created successfully!")
    
    # List created tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nCreated tables: {', '.join(tables)}")

if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)