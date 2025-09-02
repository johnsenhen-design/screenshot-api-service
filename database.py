from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This is the path to our database file. 
# It will create a file named 'app.db' in our project directory.
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# This is the main engine that connects SQLAlchemy to our database file.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# This creates a "Session" class that we will use to interact with the database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is a base class that our database models (tables) will inherit from.
Base = declarative_base()