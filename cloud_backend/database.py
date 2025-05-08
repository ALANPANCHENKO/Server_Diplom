from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Подключение к PostgreSQL
DATABASE_URL = "postgresql://gallery_user:12345@localhost:5432/cloud_gallery"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
