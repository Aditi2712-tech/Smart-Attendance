# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# # Database URL (SQLite for local dev; swap to PostgreSQL seamlessly if required)
# SQLALCHEMY_DATABASE_URL = "sqlite:///./attendance.db"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

"""
DB engine + session setup. Adjust DATABASE_URL to match your Day 1 config
(PostgreSQL in the plan, but this works unchanged for SQLite in tests).
"""

from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Uses local SQLite database file
SQLALCHEMY_DATABASE_URL = "sqlite:///./attendance.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()