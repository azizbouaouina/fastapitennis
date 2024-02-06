from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, Union


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    family_name: str
    created_at: datetime
    photo: str
    date_of_birth: date

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    datetime: datetime
    level: str
    city: str
    address: str
    description: str


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    owner_id: int
    owner: UserOut

    class Config:
        orm_mode = True


class PostOut(BaseModel):

    Post: Post
    votes: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    family_name: str
    date_of_birth: date
    gender: str
    phone_numer: Optional[str] = ""
    photo: Optional[str] = ""


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = ""
    password: Optional[str] = ""
    name: Optional[str] = ""
    family_name: Optional[str] = ""
    gender: Optional[str] = ""
    phone_numer: Optional[str] = ""


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str


class Vote(BaseModel):
    post_id: int
    dir: int
