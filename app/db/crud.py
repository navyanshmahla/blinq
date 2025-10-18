from sqlalchemy.orm import Session
from app.db.models import User, Conversation, CSVFile, Message, Plot, UsageTracking, RefreshToken
from app.db.schemas import (
    UserCreate, ConversationCreate, CSVFileCreate,
    MessageCreate, PlotCreate, UsageTrackingCreate, RefreshTokenCreate
)
from uuid import UUID
from datetime import datetime, timedelta

def create_user(db: Session, user_data: UserCreate, password_hash: str):
    user = User(
        email=user_data.email,
        password_hash=password_hash,
        full_name=user_data.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: UUID):
    return db.query(User).filter(User.id == user_id).first()

def increment_user_query_count(db: Session, user_id: UUID):
    user = get_user_by_id(db, user_id)
    if user:
        user.queries_used_this_month += 1
        db.commit()
        db.refresh(user)
    return user

def reset_monthly_query_count(db: Session, user_id: UUID):
    user = get_user_by_id(db, user_id)
    if user:
        user.queries_used_this_month = 0
        user.last_query_reset_date = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user

def create_conversation(db: Session, user_id: UUID, title: str):
    conversation = Conversation(
        user_id=user_id,
        title=title
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

def get_conversation_by_id(db: Session, conversation_id: UUID):
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def get_user_conversations(db: Session, user_id: UUID, skip: int = 0, limit: int = 100):
    return db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()

def update_conversation_title(db: Session, conversation_id: UUID, title: str):
    conversation = get_conversation_by_id(db, conversation_id)
    if conversation:
        conversation.title = title
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)
    return conversation

def link_csv_to_conversation(db: Session, conversation_id: UUID, csv_id: UUID, expires_at: datetime):
    conversation = get_conversation_by_id(db, conversation_id)
    if conversation:
        conversation.csv_id = csv_id
        conversation.csv_expires_at = expires_at
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)
    return conversation

def extend_csv_expiration(db: Session, conversation_id: UUID):
    conversation = get_conversation_by_id(db, conversation_id)
    if conversation and conversation.csv_id:
        conversation.csv_expires_at = datetime.utcnow() + timedelta(weeks=1)
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)
    return conversation

def create_csv_file(db: Session, user_id: UUID, csv_data: CSVFileCreate):
    csv_file = CSVFile(
        user_id=user_id,
        conversation_id=csv_data.conversation_id,
        filename=csv_data.filename,
        file_size=csv_data.file_size,
        row_count=csv_data.row_count,
        column_names=csv_data.column_names,
        csv_data=csv_data.csv_data,
        expires_at=csv_data.expires_at
    )
    db.add(csv_file)
    db.commit()
    db.refresh(csv_file)
    return csv_file

def get_csv_by_id(db: Session, csv_id: UUID):
    return db.query(CSVFile).filter(CSVFile.id == csv_id).first()

def get_expired_csv_files(db: Session):
    return db.query(CSVFile).filter(
        CSVFile.expires_at < datetime.utcnow(),
        CSVFile.is_deleted == False
    ).all()

def mark_csv_as_deleted(db: Session, csv_id: UUID):
    csv_file = get_csv_by_id(db, csv_id)
    if csv_file:
        csv_file.is_deleted = True
        db.commit()
        db.refresh(csv_file)
    return csv_file

def create_message(db: Session, message_data: MessageCreate):
    message = Message(
        conversation_id=message_data.conversation_id,
        role=message_data.role,
        content=message_data.content,
        cost=message_data.cost,
        request_id=message_data.request_id,
        is_plotting=message_data.is_plotting
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    conversation = get_conversation_by_id(db, message_data.conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()
        db.commit()

    return message

def get_conversation_messages(db: Session, conversation_id: UUID, skip: int = 0, limit: int = 100):
    return db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).offset(skip).limit(limit).all()

def get_message_by_id(db: Session, message_id: UUID):
    return db.query(Message).filter(Message.id == message_id).first()

def create_plot(db: Session, plot_data: PlotCreate):
    plot = Plot(
        message_id=plot_data.message_id,
        request_id=plot_data.request_id,
        image_data=plot_data.image_data
    )
    db.add(plot)
    db.commit()
    db.refresh(plot)
    return plot

def get_plot_by_request_id(db: Session, request_id: UUID):
    return db.query(Plot).filter(Plot.request_id == request_id).first()

def get_plot_by_message_id(db: Session, message_id: UUID):
    return db.query(Plot).filter(Plot.message_id == message_id).first()

def create_usage_tracking(db: Session, usage_data: UsageTrackingCreate):
    usage = UsageTracking(
        user_id=usage_data.user_id,
        message_id=usage_data.message_id,
        tokens_used=usage_data.tokens_used,
        cost=usage_data.cost,
        model_used=usage_data.model_used
    )
    db.add(usage)
    db.commit()
    db.refresh(usage)
    return usage

def get_user_usage_stats(db: Session, user_id: UUID, start_date: datetime = None, end_date: datetime = None):
    query = db.query(UsageTracking).filter(UsageTracking.user_id == user_id)

    if start_date:
        query = query.filter(UsageTracking.created_at >= start_date)
    if end_date:
        query = query.filter(UsageTracking.created_at <= end_date)

    return query.order_by(UsageTracking.created_at.desc()).all()

def get_total_user_cost(db: Session, user_id: UUID, start_date: datetime = None, end_date: datetime = None):
    query = db.query(UsageTracking).filter(UsageTracking.user_id == user_id)

    if start_date:
        query = query.filter(UsageTracking.created_at >= start_date)
    if end_date:
        query = query.filter(UsageTracking.created_at <= end_date)

    usage_records = query.all()
    return sum(record.cost for record in usage_records)

def create_refresh_token(db: Session, token_data: RefreshTokenCreate):
    refresh_token = RefreshToken(
        user_id=token_data.user_id,
        token=token_data.token,
        expires_at=token_data.expires_at
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return refresh_token

def get_refresh_token_by_token(db: Session, token: str):
    return db.query(RefreshToken).filter(RefreshToken.token == token).first()

def revoke_refresh_token(db: Session, token: str):
    refresh_token = get_refresh_token_by_token(db, token)
    if refresh_token:
        refresh_token.is_revoked = True
        db.commit()
        db.refresh(refresh_token)
    return refresh_token

def revoke_all_user_tokens(db: Session, user_id: UUID):
    tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked == False
    ).all()
    for token in tokens:
        token.is_revoked = True
    db.commit()
    return len(tokens)

def delete_expired_tokens(db: Session):
    expired = db.query(RefreshToken).filter(
        RefreshToken.expires_at < datetime.utcnow()
    ).delete()
    db.commit()
    return expired
