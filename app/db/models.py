from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, Boolean, JSON, Float, LargeBinary, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    subscription_tier = Column(Enum('free', 'pro', name='subscription_tiers'), default='free')
    queries_used_this_month = Column(Integer, default=0)
    bonus_credits = Column(Integer, default=0)
    last_query_reset_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="user")
    csv_files = relationship("CSVFile", back_populates="user", foreign_keys="CSVFile.user_id")
    usage_tracking = relationship("UsageTracking", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    csv_id = Column(UUID(as_uuid=True), ForeignKey("csv_files.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    csv_expires_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="conversations")
    csv_file = relationship("CSVFile", foreign_keys=[csv_id], post_update=True)
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class CSVFile(Base):
    __tablename__ = "csv_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    row_count = Column(Integer, nullable=False)
    column_names = Column(JSON, nullable=False)
    csv_data = Column(LargeBinary, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False)

    user = relationship("User", back_populates="csv_files", foreign_keys=[user_id])
    conversation = relationship("Conversation", foreign_keys=[conversation_id])

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(Enum('user', 'assistant', name='message_roles'), nullable=False)
    content = Column(Text, nullable=False)
    cost = Column(Float, nullable=True)
    request_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    is_plotting = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    conversation = relationship("Conversation", back_populates="messages")
    plot = relationship("Plot", back_populates="message", uselist=False, cascade="all, delete-orphan")
    usage_tracking = relationship("UsageTracking", back_populates="message", uselist=False, cascade="all, delete-orphan")

class Plot(Base):
    __tablename__ = "plots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=True, unique=True)
    request_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    image_data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    message = relationship("Message", back_populates="plot")

class UsageTracking(Base):
    __tablename__ = "usage_tracking"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False, unique=True)
    cost = Column(Float, nullable=False)
    model_used = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="usage_tracking")
    message = relationship("Message", back_populates="usage_tracking")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    is_revoked = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
