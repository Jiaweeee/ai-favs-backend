from sqlalchemy.orm import Session, defer, joinedload
from typing import List
from ...db import models
from app.apis.collection import schemas

# Collection
def get_collections(
    user_id: str,
    session: Session,
    exclude_fields: List[str] = []
):
    options = [defer(getattr(models.Collection, field)) for field in exclude_fields]
    return session.query(models.Collection)\
        .filter(
            models.Collection.user_id == user_id
        )\
        .options(*options)\
        .all()

def get_collections_by_category(
    user_id: str,
    category_id: str,
    session: Session,
    exclude_fields: List[str] = []
):
    options = [defer(getattr(models.Collection, field)) for field in exclude_fields]
    return session.query(models.Collection) \
        .filter(
            models.Collection.user_id == user_id,
            models.Collection.category_id == category_id
        ) \
        .options(*options) \
        .all()

def get_collections_by_tag(
    user_id: str,
    tag_id: str,
    session: Session,
    exclude_fields: List[str] = []
):
    field_defer_option = [defer(getattr(models.Collection, field)) for field in exclude_fields]
    collections = session.query(models.Collection) \
        .join(models.Collection.tags) \
        .filter(
            models.Tag.user_id == user_id,
            models.Tag.id == tag_id
        ) \
        .options(
            joinedload(models.Collection.tags),
            *field_defer_option
        ) \
        .all()
    return collections

def get_collection_by_id(id_: str, session: Session):
    return models.Collection.get(session=session, id_=id_)

def get_collection_by_url(
    user_id: str,
    url: str,
    session: Session
):
    return session.query(models.Collection) \
        .filter(
            models.Collection.user_id == user_id,
            models.Collection.url == url
        ) \
        .first()

def create_collection(data: schemas.CollectionCreate, session: Session):
    return models.Collection(**data.dict()).save(session)

# Tag
def get_tags(user_id: str, session: Session):
    return session.query(models.Tag) \
        .filter(
            models.Tag.user_id == user_id
        )\
        .options(joinedload(models.Tag.collections)) \
        .all()


# Category
def get_user_categories(user_id: str, session: Session):
    return session.query(models.Category) \
        .filter(models.Category.user_id == user_id) \
        .options(joinedload(models.Category.collections)) \
        .all()