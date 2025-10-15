import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# Detection models for person detection tracking
class DetectionBase(SQLModel):
    person_id: str = Field(max_length=50, index=True)  # person_1, person_2, etc.
    bbox_x1: int = Field(description="Bounding box x1 coordinate")
    bbox_y1: int = Field(description="Bounding box y1 coordinate")
    bbox_x2: int = Field(description="Bounding box x2 coordinate")
    bbox_y2: int = Field(description="Bounding box y2 coordinate")
    confidence: float = Field(ge=0.0, le=1.0, description="Detection confidence score")
    elapsed_time: float = Field(ge=0.0, description="Elapsed time in seconds since first detection")
    first_detection_time: float = Field(description="Unix timestamp of first detection")
    last_detection_time: float = Field(description="Unix timestamp of last detection")


# Properties to receive via API on creation
class DetectionCreate(DetectionBase):
    pass


# Properties to receive via API on update, all are optional
class DetectionUpdate(SQLModel):
    person_id: str | None = Field(default=None, max_length=50)
    bbox_x1: int | None = Field(default=None)
    bbox_y1: int | None = Field(default=None)
    bbox_x2: int | None = Field(default=None)
    bbox_y2: int | None = Field(default=None)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    elapsed_time: float | None = Field(default=None, ge=0.0)
    first_detection_time: float | None = Field(default=None)
    last_detection_time: float | None = Field(default=None)


# Database model, database table inferred from class name
class Detection(DetectionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Properties to return via API, id is always required
class DetectionPublic(DetectionBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class DetectionsPublic(SQLModel):
    data: list[DetectionPublic]
    count: int

