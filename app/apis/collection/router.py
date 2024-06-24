from fastapi import APIRouter, BackgroundTasks, Query, Depends, status, HTTPException
from typing import Optional
from app.apis.collection import crud
from app.apis.schemas import BaseResponse
from app.apis.dependencies import get_current_user
from .schemas import AddCollectionBody, DeleteCollectionBody, CollectionCreate
from app.utils import vectorstore, tools as Tools
from .processors import WeChatArticleProcessor
import re, logging
from app.db import database, models
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)

def is_wechat_article(url) -> bool:
    """
    Check if the url is from wechat official account article.
    """
    pattern = r'^https?://mp\.weixin\.qq\.com/s'
    if re.match(pattern, url):
        return True
    return False

def generate_and_save_category(collection_id: str, session: Session):
    logger.info("generate_and_save_category")
    collection = crud.get_collection_by_id(id_=collection_id, session=session)
    if not collection:
        raise ValueError("Collection not found.")
    categories = crud.get_user_categories(session=session, user_id=collection.user_id)
    if not categories:
        category_names = []
    else:
        category_names = list(map(lambda x: x.name, categories))
    response = Tools.classification_tool(collection.content, category_names)
    try:
        category_name = response["name"]
        category_desc = response["description"]
        category = session.query(models.Category).filter(
            models.Category.name == category_name,
            models.Category.user_id == collection.user_id
        ).first()
        if not category:
            category = models.Category(
                name=category_name,
                description=category_desc,
                user_id=collection.user_id
            ).save(session=session)
        collection.category_id = category.id
        session.commit()
        logger.info(f"generate_category done. category = {category_name}")
    except Exception as e:
        logger.error(f"generate_category failed, error: {e}")

def generate_and_save_tags(collection_id: str, session: Session):
    logger.info("generate_and_save_tags")
    collection = crud.get_collection_by_id(id_=collection_id, session=session)
    if not collection:
        raise ValueError("Collection not found.")
    response = Tools.tagging_tool(collection.content)
    try:
        tag_names = response.get("tags", None)
        if not tag_names:
            return
        tags = []
        for name in tag_names:
            tag = session.query(models.Tag).filter(
                models.Tag.name == name,
                models.Tag.user_id == collection.user_id
            ).first()
            if not tag:
                tag = models.Tag(
                    name=name,
                    user_id=collection.user_id
                )
                session.add(tag)
            tags.append(tag)
        collection.tags.extend(tags)
        session.commit()
        logger.info(f"generate_tags, done. tags = {tag_names}")
    except Exception as e:
        logger.error(f"generate_tags failed, error: {e}")

def generate_and_save_summary(collection_id: str, session: Session):
    logger.info("generate_and_save_summary")
    collection = crud.get_collection_by_id(id_=collection_id, session=session)
    if not collection:
        raise ValueError("Collection not found.")
    summary = Tools.summary_tool(collection.content)
    if summary:
        collection.summary = summary
        session.commit()
    logger.info(f"summary = {summary}")

def save_to_vector_store(collection_id: str, session: Session):
    collection = crud.get_collection_by_id(id_=collection_id, session=session)
    if not collection:
        raise ValueError("Collection not found.")
    if collection.content:
        logger.info(f"Saving content to vector store. url = {collection.url}, user_id = {collection.user_id}")
        vectorstore.save_content_to_index(
            content=collection.content,
            index_name=collection.user_id,
            metadata={
                "content_id": collection.id,
                "source": collection.url
            }
        )
        logger.info(f"Save content to vector store, Done. url = {collection.url}")

@router.post("/collection/add", response_model=BaseResponse)
async def add_collection(
    body: AddCollectionBody,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db_session),
    current_user: models.User = Depends(get_current_user)
):
    if not is_wechat_article(body.url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content not support."
        )
    url = body.url
    processor = WeChatArticleProcessor()
    item = crud.get_collection_by_url(
        user_id=current_user.id,
        url=url,
        session=db
    )
    if item:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Content already exists."
        )
    else:
        data = await processor.run_async(url)
        new_collection = crud.create_collection(
            data=CollectionCreate(**data, user_id=current_user.id),
            session=db
        )
        background_tasks.add_task(generate_and_save_tags, new_collection.id, db)
        background_tasks.add_task(generate_and_save_summary, new_collection.id, db)
        background_tasks.add_task(generate_and_save_category, new_collection.id, db)
        background_tasks.add_task(save_to_vector_store, new_collection.id, db)
        return BaseResponse(
            code=status.HTTP_200_OK,
            msg='success'
        )

@router.get("/collection/list/get", response_model=BaseResponse)
def get_collection_list(
    category_id: Optional[str]=Query(None),
    tag_id: Optional[str]=Query(None),
    db: Session = Depends(database.get_db_session),
    current_user: models.User = Depends(get_current_user)
):
    exclude_fields = ["category_id", "content", "user_id"]
    if category_id:
        items = crud.get_collections_by_category(
            user_id=current_user.id,
            category_id=category_id,
            session=db,
            exclude_fields=exclude_fields
        )
    elif tag_id:
        items = crud.get_collections_by_tag(
            user_id=current_user.id,
            tag_id=tag_id,
            session=db,
            exclude_fields=exclude_fields
        )
    else:
        items = crud.get_collections(
            user_id=current_user.id,
            session=db,
            exclude_fields=exclude_fields
        )
    return BaseResponse(
        code=status.HTTP_200_OK,
        msg='success',
        data=items
    )

@router.get("/collection/overview")
def get_collection_overview(
    db: Session = Depends(database.get_db_session),
    current_user: models.User = Depends(get_current_user)
):
    # get categories
    db_categories = crud.get_user_categories(
        session=db,
        user_id=current_user.id
    )
    categories = [
        {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "collection_count": len(category.collections)
        }
        for category in db_categories
    ]
    # get tags
    db_tags = crud.get_tags(
        user_id=current_user.id,
        session=db
    )
    tags = [
        {
            "id": tag.id,
            "name": tag.name,
            "collection_count": len(tag.collections)
        }
        for tag in db_tags
    ]
    return BaseResponse(
        code=status.HTTP_200_OK,
        msg="success",
        data={
            "categories": categories,
            "tags": tags
        }
    )


__all__ = ["router"]