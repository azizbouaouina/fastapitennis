
from .. import models, schemas, utils, oauth2
from sqlalchemy.orm import Session
from fastapi import Response, status, HTTPException, Depends, APIRouter, File, UploadFile
from ..database import get_db
import uuid


router = APIRouter(prefix="/users",
                   tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED,)
def create_users(user: schemas.UserCreate, db: Session = Depends(get_db)):

    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())

    user = db.query(models.User).filter(
        models.User.email == new_user.email).first()

    if user:
        raise HTTPException(status_code=status.HTTP_226_IM_USED,
                            detail="Email already used")

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = oauth2.create_access_token(data={"user_id": new_user.id})

    return {"access_token": access_token, "token_type": "bearer", "user_id": new_user.id}


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id {id} was not found")
    if id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'user with id {current_user.id} is not authorized to access this')

    return user


@router.put("/{id}", status_code=status.HTTP_201_CREATED,
            response_model=schemas.UserOut)
async def update_user(id: int, updated_user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id {id} does not exist")

    if id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'user with id {current_user.id} is not authorized to access this')

    user_query.update(updated_user.dict(), synchronize_session=False)
    db.commit()
    return user_query.first()


IMAGEDIR = "./static/images/"


@router.put("/{id}/upload/", status_code=status.HTTP_201_CREATED,
            response_model=schemas.UserOut)
async def update_photo_user(id: int, db: Session = Depends(get_db), file: UploadFile = File(...)):

    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id {id} does not exist")

    file.filename = f"{uuid.uuid4()}.jpg"
    contents = await file.read()

    print(f"{IMAGEDIR}{file.filename}")

    # save the file
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)

    user_query.update({models.User.photo: file.filename},
                      synchronize_session=False)
    db.commit()
    return user_query.first()
