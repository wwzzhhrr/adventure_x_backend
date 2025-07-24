from app.database import engine
from app.models.user import Base
from sqlalchemy import text

# Drop existing tables and recreate them
with engine.connect() as conn:
    # Drop the users table if it exists
    conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
    conn.commit()
    print("Dropped existing users table")

# Create all tables with the correct schema
Base.metadata.create_all(bind=engine)
print("Database tables created successfully with correct schema!")