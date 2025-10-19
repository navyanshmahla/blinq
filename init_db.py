from app.db.database import engine, Base
from app.db.models import User, Conversation, CSVFile, Message, Plot, UsageTracking, RefreshToken

def init_database():
    """Initialize database by creating all tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully at blinq.db")

if __name__ == "__main__":
    init_database()
