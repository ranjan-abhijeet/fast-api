import psycopg2
import time

from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Response, HTTPException, status, Depends
from pydantic import BaseModel
from dotenv import dotenv_values
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind=engine)
app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    publish: bool = True


@app.get("/posts", status_code=status.HTTP_200_OK)
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.get("/posts/{id}", status_code=status.HTTP_200_OK)
def get_post_by_id(id: int, db: Session = Depends(get_db)):
    return_data = db.query(models.Post).filter(
        models.Post.post_id == id).first()

    if not return_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")
    return {"message": return_data}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {
        "message": "successfully created post",
        "data": new_post
    }


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    delete_query = db.query(models.Post).filter(models.Post.post_id == id)
    post = delete_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")

    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_entire_post(id: int, post: Post, db: Session = Depends(get_db)):
    update_query = db.query(models.Post).filter(models.Post.post_id == id)
    update_post = update_query.first()
    if update_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")

    update_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return {
        "message": f"successfully updated post: {id}",
        "data": update_query.first()
    }
