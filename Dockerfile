# FROM python:3.9.7

# WORKDIR /usr/src/app

# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# # Set environment variables
# ENV DATABASE_HOSTNAME=192.168.1.18
# ENV DATABASE_PORT=5432
# ENV DATABASE_PASSWORD=aziz
# ENV DATABASE_NAME=fastapi
# ENV DATABASE_USERNAME=postgres
# ENV SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
# ENV ALGORITHM=HS256
# ENV ACCESS_TOKEN_EXPIRE_MINUTES=60

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.9.7
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
