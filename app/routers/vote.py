from typing import List
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from fastapi import Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from typing import Optional

router = APIRouter(prefix="/votes",
                   tags=["Votes"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_posts(vote: schemas.Vote, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(
        models.Post.id == vote.post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {vote.post_id} was not found")

    vote_query = db.query(models.Vote).filter(models.Vote.user_id == current_user.id,
                                              models.Vote.post_id == vote.post_id)
    vote_check = vote_query.first()

    if vote.dir == 1:

        if vote_check:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"user with id {current_user.id} has already voted on post with id {vote.post_id}")

        new_vote = models.Vote(user_id=current_user.id, post_id=vote.post_id)
        db.add(new_vote)
        db.commit()
        return {"message ": "sucessfuly added vote"}

    else:
        if not vote_check:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"vote does not exist")

        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message ": "sucessfuly deleted vote"}
