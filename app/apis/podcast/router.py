from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status as HttpStatus
from .schemas import PodcastCreateRequestBody, PodcastResponse
from app.utils import tts as TTS
from app.db import database, models
from app.apis.schemas import BaseResponse
from app.apis.podcast import crud as CRUD
from app.apis.dependencies import get_current_user
from sqlalchemy.orm import Session

router = APIRouter()

def generate_podcast_audio(podcast_id: str, db_session: Session):
    podcast = CRUD.get_podcast(id_=podcast_id, session=db_session)
    collection = podcast.collection
    audio_file = TTS.text_to_speech(
        text=collection.content,
        output_dir='app/public/audio',
        identifier=podcast.id
    )
    if audio_file:
        podcast.file_path = f"/audio/{audio_file}"
        podcast.status = models.PodcastStatus.COMPLETE.value
    else:
        podcast.status = models.PodcastStatus.ERROR.value
    podcast.save(db_session)

@router.post("/podcast/create", response_model=BaseResponse)
async def create_podcast(
    body: PodcastCreateRequestBody,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(database.get_db_session),
    current_user: models.User = Depends(get_current_user)
):
    collection_id = body.collection_id
    collection = models.Collection.get(
        id_=collection_id,
        session=db_session
    )
    if not collection:
        raise HTTPException(
            status_code=HttpStatus.HTTP_404_NOT_FOUND,
            detail="Collection not found."
        )
    if collection.user_id != current_user.id:
        raise HTTPException(
            status_code=HttpStatus.HTTP_400_BAD_REQUEST,
            detail="Invalid collection id."
        )
    if not collection.podcast:
        podcast = CRUD.create_podcast_from_collection(
            collection_id=collection_id,
            session=db_session
        )
    else:
        podcast_status = collection.podcast.status
        if podcast_status == models.PodcastStatus.ERROR.value:
            podcast = collection.podcast
            podcast.status = models.PodcastStatus.GENERATING.value
            podcast.save(db_session)
        elif podcast_status == models.PodcastStatus.GENERATING.value:
            return BaseResponse(
                code=HttpStatus.HTTP_200_OK,
                msg="Podcast generation in progress, please check again later."
            )
        else:
            raise HTTPException(
                status_code=HttpStatus.HTTP_409_CONFLICT,
                detail="Podcast already created."
            )
    background_tasks.add_task(generate_podcast_audio, podcast.id, db_session)
    return BaseResponse(
        code=HttpStatus.HTTP_200_OK,
        msg="success"
    )
    
@router.get("/podcast/list/get", response_model=BaseResponse)
async def get_podcast_list(
    db_session: Session = Depends(database.get_db_session),
    current_user: models.User = Depends(get_current_user)
):
    db_podcasts = CRUD.get_podcast_list(
        user_id=current_user.id,
        session=db_session
    )
    def to_podcast_response(item: models.Podcast):
        return PodcastResponse(
            id=item.id,
            title=item.title,
            status=item.status,
            file_path=item.file_path,
            transcript=item.transcript,
            collection_id=item.collection.id,
            collection_url=item.collection.url
        )

    podcasts = list(map(lambda x: to_podcast_response(x), db_podcasts))
    return BaseResponse(
        code=HttpStatus.HTTP_200_OK,
        data=podcasts
    )

__all__ = ["router"]