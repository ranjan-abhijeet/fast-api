from fastapi import Response, HTTPException, status, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["POSTS"]
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.PostWithVote])
def get_posts(db: Session = Depends(get_db),
              current_user: int = Depends(oauth2.get_current_user),
              limit: int = 10,
              skip: int = 0,
              search: Optional[str] = ""):

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
                models.Vote, models.Vote.post_id == models.Post.post_id, isouter=True).group_by(
                models.Post.post_id).filter(models.Post.title.contains(search)).limit(
                limit=limit).offset(offset=skip).all()
    return posts


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostWithVote)
def get_post_by_id(id: int,
                   db: Session = Depends(get_db),
                   current_user: int = Depends(oauth2.get_current_user)):


    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
                models.Vote, models.Vote.post_id == models.Post.post_id, isouter=True).group_by(
                models.Post.post_id).filter(models.Post.post_id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    new_post = models.Post(owner_id=current_user.user_id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    delete_query = db.query(models.Post).filter(models.Post.post_id == id)
    post = delete_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")

    elif post.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="not authorised to perform requested action")

    delete_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.PostResponse)
def update_entire_post(id: int,
                       post: schemas.PostCreate,
                       db: Session = Depends(get_db),
                       current_user: int = Depends(oauth2.get_current_user)):
    update_query = db.query(models.Post).filter(models.Post.post_id == id)
    post = update_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")

    elif post.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="not authorised to perform requested action")

    update_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return update_query.first()
