from fastapi import APIRouter, BackgroundTasks, Depends
from .schemas import PodcastCreateRequestBody, PodcastResponse
from app.utils import tts as TTS
from app.db import database, models
from app.apis.schemas import BaseResponse
from app.apis.podcast import crud as CRUD
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
    db_session: Session = Depends(database.get_db_session)
):
    collection_id = body.collection_id
    collection = models.Collection.get(
        id_=collection_id,
        session=db_session
    )
    if not collection.podcast:
        podcast = CRUD.create_podcast_from_collection(
            collection_id=collection_id,
            session=db_session
        )
    else:
        status = collection.podcast.status
        if status == models.PodcastStatus.ERROR.value:
            podcast = collection.podcast
            podcast.status = models.PodcastStatus.GENERATING.value
            podcast.save(db_session)
        elif status == models.PodcastStatus.GENERATING.value:
            return BaseResponse(
                code=200,
                msg="Podcast generation in progress, please check again later."
            )
        else:
            return BaseResponse(
                code=500,
                msg="Podcast already created."
            )
    background_tasks.add_task(generate_podcast_audio, podcast.id, db_session)
    return BaseResponse(
        code=200,
        msg="success"
    )
    
@router.get("/podcast/list/get", response_model=BaseResponse)
async def get_podcast_list(db_session: Session = Depends(database.get_db_session)):
    db_podcasts = CRUD.get_podcast_list(db_session)
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
        code=200,
        data=podcasts
    )

__all__ = ["router"]