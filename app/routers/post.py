import os
from typing import List
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from fastapi import Response, status, HTTPException, Depends, APIRouter, File, UploadFile
from ..database import get_db
from typing import Optional
from sqlalchemy import func
from datetime import datetime, date
import uuid
from fastapi.responses import FileResponse


router = APIRouter(prefix="/posts",
                   tags=["Posts"])


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db),
              limit: int = 10, skip: int = 0, search: Optional[str] = "",):

    posts = db.query(models.Post,
                     func.count(models.Vote.post_id).label("votes"),
                     func.array_agg(models.Vote.user_id).label("voter_ids"),
                     func.array_agg(models.Vote.accepted).label(
                         "accepted"),

                     ).join(
                         models.Vote, models.Vote.post_id == models.Post.id,
                         isouter=True
    ).group_by(
        models.Post.id
    ).filter(
        models.Post.city.contains(search)).limit(limit).offset(skip).all()

    liste = []
    for p in posts:
        liste.append(p._asdict())

    return liste

# get filtered posts


@router.get("/filtered/", response_model=List[schemas.PostOut])
def get__filtered_posts(db: Session = Depends(get_db), datetime_filter: date = None,
                        level_filter: str = None, city_filter: str = None):

    # Calculate the start and end of the specified day
    datetime_start = datetime.combine(datetime_filter, datetime.min.time())
    datetime_end = datetime.combine(datetime_filter, datetime.max.time())

    posts = (
        db.query(models.Post,
                 func.count(models.Vote.post_id).label("votes"),
                 func.array_agg(models.Vote.user_id).label("voter_ids"),
                 func.array_agg(models.Vote.accepted).label(
                     "accepted"),)
        .join(
            models.Vote, models.Vote.post_id == models.Post.id, isouter=True
        )
        .group_by(models.Post.id)
        .filter(models.Post.datetime >= datetime_start)
        .filter(models.Post.datetime <= datetime_end)
        .filter(models.Post.level == level_filter)
        .filter(models.Post.city == city_filter)
        .all()
    )
    liste = []
    for p in posts:
        liste.append(p._asdict())

    return liste


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    post = db.query(models.Post,
                    func.count(models.Vote.post_id).label("votes"),
                    func.array_agg(models.Vote.user_id).label("voter_ids"),
                    func.array_agg(models.Vote.accepted).label(
                        "accepted"),
                    ).join(
        models.Vote,
        models.Vote.post_id == models.Post.id,
        isouter=True
    ).group_by(
        models.Post.id
    ).filter(
        models.Post.id == id
    ).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} was not found")

    if post.Post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"user with id {current_user.id} is unothorized to access this post")

    return post._asdict()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def del_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} does not exist")

    if post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"user with id {current_user.id} is unothorized to delete this post")

    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"user with id {current_user.id} is unothorized to update this post")

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


IMAGEDIR = "./static/images/"


@router.post("/upload/", status_code=status.HTTP_201_CREATED, )
async def create_upload_file(file: UploadFile = File(...)):

    file.filename = f"{uuid.uuid4()}.jpg"
    contents = await file.read()

    print(f"{IMAGEDIR}{file.filename}")

    # save the file
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)

    return {"filename": file.filename}
