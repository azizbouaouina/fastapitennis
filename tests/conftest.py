from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import Base, get_db
import pytest
from app.models import User
from app.oauth2 import create_access_token
from app import models

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}"
    f":{settings.database_port}/{settings.database_name}_test"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "aziz@gmail.com", "password": "password"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    user = res.json()
    user['password'] = user_data['password']
    return user


@pytest.fixture
def token(test_user):
    id = test_user["id"]
    created_token = create_access_token({"user_id": id})
    return created_token


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


@pytest.fixture
def test_posts(test_user, session):

    session.add_all([models.Post(title="first title", content="first content", owner_id=test_user['id']),
                    models.Post(title="2nd title",
                                content="2nd content", owner_id=test_user['id']),
                    models.Post(title="3rd title", content="3rd content", owner_id=test_user['id'])])
    session.commit()

    posts = session.query(models.Post).all()
    return posts
