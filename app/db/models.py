import uuid, enum
from sqlalchemy import String, Text, ForeignKey, Table, Column, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from typing import Optional, Type, TypeVar

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

class Collection(Base):
    __tablename__ = "collections"

    url: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
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

class Tag(Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    collections: Mapped[list["Collection"]] = relationship(
        secondary="collections_tags",
        back_populates="tags"
    )

class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    collections: Mapped[list["Collection"]] = relationship(back_populates="category")

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

collections_tags = Table("collections_tags", Base.metadata,
    Column("collection_id", String(255), ForeignKey("collections.id"), primary_key=True),
    Column("tag_id", String(255), ForeignKey("tags.id"), primary_key=True)
)