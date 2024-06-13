from .schemas import PodcastCreate
from app.db.models import Collection, Podcast, PodcastStatus
from sqlalchemy.orm import Session

def get_podcast(id_: str, session: Session):
    podcast = Podcast.get(id_=id_, session=session)
    if podcast:
        return podcast
    raise ValueError("Podcast not found.")

def get_podcast_list(session: Session):
    return session.query(Podcast).all()

def create_podcast_from_collection(
    collection_id: str,
    session: Session
):
    collection = Collection.get(session=session, id_=collection_id)
    if not collection:
        raise ValueError("Collection not found.")
    create_obj = PodcastCreate(
        title=collection.title,
        status=PodcastStatus.GENERATING.value
    )
    podcast = Podcast(**create_obj.dict())
    podcast.collection = collection
    return podcast.save(session)

def delete_podcast(id_: str, session: Session):
    podcast = Podcast.get(id_=id_, session=session)
    if podcast:
        podcast.delete(session)
    else:
        raise ValueError("Podcast does not exist.")