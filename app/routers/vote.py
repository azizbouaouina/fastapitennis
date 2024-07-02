from typing import List
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from fastapi import Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from typing import Optional

router = APIRouter(prefix="/votes",
                   tags=["Votes"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_votes(vote: schemas.Vote, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

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


# response_model = List[schemas.UserOut]
@router.get("/{post_id}", response_model=List[schemas.UserOut])
def get_request(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(
        models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"user with id {current_user.id} is unothorized to access this post")

    request = db.query(models.User
                       ).join(
        models.Vote,
        models.Vote.user_id == models.User.id,
        isouter=True
    ).filter(
        models.Vote.post_id == post_id
    ).all()

    if not request:
        return []

    liste = []
    for r in request:
        liste.append(r)

    return liste


@router.delete("/deleted", status_code=status.HTTP_204_NO_CONTENT)
def del_request(user_id: int, post_id, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    request = db.query(models.Vote).filter(models.Vote.user_id ==
                                           user_id).filter(models.Vote.post_id == post_id)
    if not request.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"request not found")

    request.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/accepted", )
def del_requests(user_id: int, post_id, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    request = db.query(models.Vote).filter(models.Vote.user_id !=
                                           user_id).filter(models.Vote.post_id == post_id)
    # if not request.first():
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f"requests not found")
    if request.first():
        request.delete(synchronize_session=False)
        db.commit()

    return Response(status_code=status.HTTP_200_OK)


@router.put("/accepted")
def accept_request(user_id: int, post_id, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    request = db.query(models.Vote).filter(models.Vote.user_id ==
                                           user_id).filter(models.Vote.post_id == post_id).first()
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"request not found")

    request.accepted = True
    db.commit()
    db.refresh(request)
    return request
