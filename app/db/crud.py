from sqlalchemy.orm import Session
from . import models, schemas, database

# Collection
def get_collections(session: Session):
    return session.query(models.Collection).all()

def get_collections_by_category(category_id: str, session: Session):
    return session.query(models.Collection) \
        .filter(models.Collection.category_id == category_id) \
        .all()

def get_collections_by_tag(tag_id: str, session: Session):
    tag = session.query(models.Tag) \
        .filter(models.Tag.id == tag_id) \
        .first()
    return tag.collections

def get_collection_by_id(id_: str, session: Session):
    return models.Collection.get(session=session, id_=id_)

def get_collection_by_url(url: str, session: Session):
    return session.query(models.Collection) \
        .filter(models.Collection.url == url) \
        .first()

def create_collection(data: schemas.CollectionCreate, session: Session):
    return models.Collection(**data.dict()).save(session)

def update_collection(
        id_: str,
        data: schemas.Collection,
        session: Session
):
    db_collection = session.query(models.Collection) \
        .filter(models.Collection.id == id_) \
        .first()
    if not db_collection:
        raise ValueError("Collection not found.")
    for key, value in data.dict():
        if hasattr(db_collection, key):
            setattr(db_collection, key, value)
        else:
            raise ValueError(f"Invalid field: {key}")
    session.commit()
    session.refresh(db_collection)
    return db_collection

# Tag
def create_tags():
    pass

# Category
def get_catetories(session: Session):
    return session.query(models.Category).all()