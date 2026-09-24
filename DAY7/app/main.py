from fastapi import FastAPI
from app.database import Base, engine

app = FastAPI(title="Day 7 Project Management API")

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Day 7 Project Management API is running"}
