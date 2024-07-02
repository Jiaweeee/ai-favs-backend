import uuid, enum
from sqlalchemy import String, Text, ForeignKey, Table, Column, Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from typing import Optional, Type, TypeVar
from datetime import datetime, timezone

T = TypeVar("T", bound="Base")

class Base(DeclarativeBase):
    """Base for all models."""
    
    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda _: str(uuid.uuid4()),
        unique=True,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    @classmethod
    def get(cls: Type[T], session: Session, id_: str) -> Optional[T]:
        return session.get(cls, id_)
    
    def save(self: T, session: Session) -> T:
        session.add(self)
        session.commit()
        session.refresh(self)
        return self
    
    def delete(self: T, session: Session) -> None:
        session.delete(self)
        session.commit()

class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=True)

class Collection(Base):
    __tablename__ = "collections"

    url: Mapped[str] = mapped_column(String(255), unique=False, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    thumbnail_url: Mapped[str] = mapped_column(String(512), nullable=True, default=None)
    content: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    summary: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.id"), nullable=True, default=None)
    category: Mapped["Category"] = relationship(
        back_populates="collections",
        lazy="selectin"
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary="collections_tags",
        back_populates="collections",
        lazy="selectin"
    )
    podcast_id: Mapped[str] = mapped_column(ForeignKey("podcasts.id"), unique=True, nullable=True)
    podcast: Mapped["Podcast"] = relationship(
        back_populates="collection",
        uselist=False,
        lazy="selectin"
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

class Tag(Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(16), unique=False, nullable=False)
    collections: Mapped[list["Collection"]] = relationship(
        secondary="collections_tags",
        back_populates="tags"
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(64), unique=False, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    collections: Mapped[list["Collection"]] = relationship(back_populates="category")
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

class PodcastStatus(enum.Enum):
    GENERATING = 1
    COMPLETE = 2
    ERROR = -1

class Podcast(Base):
    __tablename__ = "podcasts"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    transcript: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=PodcastStatus.GENERATING.value
    )
    collection: Mapped["Collection"] = relationship(
        back_populates="podcast"
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

collections_tags = Table("collections_tags", Base.metadata,
    Column("collection_id", String(255), ForeignKey("collections.id"), primary_key=True),
    Column("tag_id", String(255), ForeignKey("tags.id"), primary_key=True)
)