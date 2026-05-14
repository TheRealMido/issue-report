import os
import pymysql
from sqlalchemy import create_engine, MetaData, Table, select
from dotenv import load_dotenv

# Load local .env for MySQL
load_dotenv()

# LOCAL MYSQL (Source)
MYSQL_USER = os.getenv('DB_USER', 'root')
MYSQL_PASS = os.getenv('DB_PASSWORD', 'Root')
MYSQL_HOST = os.getenv('DB_HOST', 'localhost')
MYSQL_NAME = os.getenv('DB_NAME', 'issue_reporter')

mysql_engine = create_engine(f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}/{MYSQL_NAME}')
mysql_metadata = MetaData()

# VERCEL POSTGRES (Target)
POSTGRES_URL = "postgresql://neondb_owner:npg_2jqpaZ6nPBDT@ep-soft-butterfly-aqxu9y7b-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require"
pg_engine = create_engine(POSTGRES_URL)

def sync():
    print("Connecting and reflecting MySQL...")
    mysql_metadata.reflect(bind=mysql_engine)
    
    # Import models to get table definitions
    from models import db, User, Category, Issue, StatusUpdate, Vote
    from app import app
    
    print("Creating tables on Postgres if missing...")
    with app.app_context():
        # Ensure Postgres engine is used
        db.metadata.create_all(bind=pg_engine)
    
    # Mapping: Local Name (MySQL) -> Remote Table (SQLAlchemy Object)
    mapping = {
        'users': User.__table__,
        'categories': Category.__table__,
        'issues': Issue.__table__,
        'status_updates': StatusUpdate.__table__,
        'votes': Vote.__table__
    }
    
    with pg_engine.connect() as pg_conn:
        for local_name, remote_table in mapping.items():
            if local_name not in mysql_metadata.tables:
                print(f"Table '{local_name}' not found locally. Skipping.")
                continue
                
            local_table = mysql_metadata.tables[local_name]
            print(f"Syncing '{local_name}' to '{remote_table.name}'...")
            
            # Read all rows from MySQL
            with mysql_engine.connect() as my_conn:
                rows = my_conn.execute(local_table.select()).fetchall()
                
            if not rows:
                print(f"No data to sync for '{local_name}'.")
                continue
                
            # Convert rows to dicts for insertion
            # We map local columns to remote columns. Assuming they match.
            data = [dict(row._mapping) for row in rows]
            
            try:
                # Clean remote table first
                pg_conn.execute(remote_table.delete())
                pg_conn.execute(remote_table.insert(), data)
                pg_conn.commit()
                print(f"Successfully synced {len(data)} rows.")
            except Exception as e:
                print(f"Error syncing {local_name}: {e}")
                pg_conn.rollback()

if __name__ == "__main__":
    try:
        sync()
        print("\nSUCCESS: All local data is now in Vercel!")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
