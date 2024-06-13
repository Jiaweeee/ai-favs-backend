from sqlalchemy.orm import Session, defer, joinedload
from typing import List
from . import models, schemas

# Collection
def get_collections(session: Session, exclude_fields: List[str] = []):
    options = [defer(getattr(models.Collection, field)) for field in exclude_fields]
    return session.query(models.Collection).options(*options).all()

def get_collections_by_category(category_id: str, session: Session, exclude_fields: List[str] = []):
    options = [defer(getattr(models.Collection, field)) for field in exclude_fields]
    return session.query(models.Collection) \
        .filter(models.Collection.category_id == category_id) \
        .options(*options) \
        .all()

def get_collections_by_tag(tag_id: str, session: Session, exclude_fields: List[str] = []):
    field_defer_option = [defer(getattr(models.Collection, field)) for field in exclude_fields]
    collections = session.query(models.Collection) \
        .join(models.Collection.tags) \
        .filter(models.Tag.id == tag_id) \
        .options(
            joinedload(models.Collection.tags),
            *field_defer_option
        ) \
        .all()
    return collections

def get_collection_by_id(id_: str, session: Session):
    return models.Collection.get(session=session, id_=id_)

def get_collection_by_url(url: str, session: Session):
    return session.query(models.Collection) \
        .filter(models.Collection.url == url) \
        .first()

def create_collection(data: schemas.CollectionCreate, session: Session):
    return models.Collection(**data.dict()).save(session)

# Tag
def get_tags(session: Session):
    return session.query(models.Tag) \
        .options(joinedload(models.Tag.collections)) \
        .all()


# Category
def get_catetories(session: Session):
    return session.query(models.Category) \
        .options(joinedload(models.Category.collections)) \
        .all()