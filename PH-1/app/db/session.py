from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import os
import logging

logger = logging.getLogger(__name__)

# Database configuration
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'docdb')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

# Force database type via environment variable
FORCE_DB_TYPE = os.getenv('DB_TYPE', 'auto')  # 'auto', 'postgresql', 'sqlite'

def get_database_config():
    """Determine which database to use and return the appropriate configuration"""
    
    if FORCE_DB_TYPE == 'sqlite':
        return create_sqlite_config()
    elif FORCE_DB_TYPE == 'postgresql':
        return create_postgresql_config()
    else:  # auto
        # Try PostgreSQL first, fallback to SQLite
        try:
            config = create_postgresql_config()
            # Test the connection
            test_engine = create_engine(config['url'])
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Using PostgreSQL database")
            return config
        except OperationalError as e:
            logger.warning(f"PostgreSQL connection failed: {e}")
            logger.info("Falling back to SQLite database")
            return create_sqlite_config()

def create_postgresql_config():
    """Create PostgreSQL database configuration"""
    database_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    return {
        'url': database_url,
        'engine_args': {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        },
        'type': 'postgresql'
    }

def create_sqlite_config():
    """Create SQLite database configuration"""
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    database_path = os.path.join(data_dir, 'explainium.db')
    database_url = f"sqlite:///{database_path}"
    
    return {
        'url': database_url,
        'engine_args': {
            'pool_pre_ping': True,
            'connect_args': {"check_same_thread": False}
        },
        'type': 'sqlite'
    }

# Initialize database configuration
db_config = get_database_config()
DATABASE_URL = db_config['url']
DATABASE_TYPE = db_config['type']

# Create engine with appropriate configuration
if DATABASE_TYPE == 'sqlite':
    engine = create_engine(
        DATABASE_URL,
        **db_config['engine_args']
    )
else:
    engine = create_engine(
        DATABASE_URL,
        **db_config['engine_args']
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_info():
    """Get information about the current database configuration"""
    return {
        'type': DATABASE_TYPE,
        'url': DATABASE_URL.replace(POSTGRES_PASSWORD, '***') if 'postgresql' in DATABASE_URL else DATABASE_URL,
        'status': 'connected'
    } 