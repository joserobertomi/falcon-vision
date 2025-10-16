import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate, Detection, DetectionCreate, DetectionUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# Detection CRUD operations
def create_detection(*, session: Session, detection_in: DetectionCreate) -> Detection:
    """Create a new detection record."""
    db_detection = Detection.model_validate(detection_in)
    session.add(db_detection)
    session.commit()
    session.refresh(db_detection)
    return db_detection


def get_detection_by_id(*, session: Session, detection_id: uuid.UUID) -> Detection | None:
    """Get a detection by its ID."""
    statement = select(Detection).where(Detection.id == detection_id)
    db_detection = session.exec(statement).first()
    return db_detection


def get_detections_by_person_id(*, session: Session, person_id: str) -> list[Detection]:
    """Get all detections for a specific person ID."""
    statement = select(Detection).where(Detection.person_id == person_id)
    db_detections = session.exec(statement).all()
    return list(db_detections)


def get_detections(*, session: Session, skip: int = 0, limit: int = 100) -> list[Detection]:
    """Get detections with pagination."""
    statement = select(Detection).offset(skip).limit(limit)
    db_detections = session.exec(statement).all()
    return list(db_detections)


def update_detection(*, session: Session, db_detection: Detection, detection_in: DetectionUpdate) -> Detection:
    """Update an existing detection."""
    detection_data = detection_in.model_dump(exclude_unset=True)
    db_detection.sqlmodel_update(detection_data)
    session.add(db_detection)
    session.commit()
    session.refresh(db_detection)
    return db_detection


def delete_detection(*, session: Session, detection_id: uuid.UUID) -> Detection | None:
    """Delete a detection by ID."""
    statement = select(Detection).where(Detection.id == detection_id)
    db_detection = session.exec(statement).first()
    if db_detection:
        session.delete(db_detection)
        session.commit()
    return db_detection


def get_detections_by_time_range(*, session: Session, start_time: datetime, end_time: datetime) -> list[Detection]:
    """Get detections within a specific time range."""
    statement = select(Detection).where(
        Detection.detection_time >= start_time,
        Detection.detection_time <= end_time
    )
    db_detections = session.exec(statement).all()
    return list(db_detections)


def get_detections_by_confidence(*, session: Session, min_confidence: float) -> list[Detection]:
    """Get detections with confidence above a threshold."""
    statement = select(Detection).where(Detection.confidence >= min_confidence)
    db_detections = session.exec(statement).all()
    return list(db_detections)


def get_latest_detection_by_person_id(*, session: Session, person_id: str) -> Detection | None:
    """Get the latest detection for a specific person ID."""
    statement = select(Detection).where(Detection.person_id == person_id).order_by(Detection.detection_time.desc())
    db_detection = session.exec(statement).first()
    return db_detection


def get_first_detection_by_person_id(*, session: Session, person_id: str) -> Detection | None:
    """Get the first detection for a specific person ID."""
    statement = select(Detection).where(Detection.person_id == person_id).order_by(Detection.detection_time.asc())
    db_detection = session.exec(statement).first()
    return db_detection


def get_person_detection_stats(*, session: Session, person_id: str) -> dict:
    """Get detection statistics for a specific person ID."""
    from sqlmodel import func
    
    # Get first and last detection times
    first_detection = get_first_detection_by_person_id(session=session, person_id=person_id)
    last_detection = get_latest_detection_by_person_id(session=session, person_id=person_id)
    
    if not first_detection or not last_detection:
        return {
            "person_id": person_id,
            "first_detection_time": None,
            "last_detection_time": None,
            "elapsed_time": 0.0,
            "detection_count": 0
        }
    
    # Calculate elapsed time
    elapsed_time = (last_detection.detection_time - first_detection.detection_time).total_seconds()
    
    # Get total detection count
    count_statement = select(func.count()).select_from(Detection).where(Detection.person_id == person_id)
    detection_count = session.exec(count_statement).one()
    
    return {
        "person_id": person_id,
        "first_detection_time": first_detection.detection_time,
        "last_detection_time": last_detection.detection_time,
        "elapsed_time": elapsed_time,
        "detection_count": detection_count
    }
