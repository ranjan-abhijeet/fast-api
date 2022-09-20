from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import database, oauth2, schemas, models

router = APIRouter(
    prefix="/vote",
    tags=["Votes"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote_post(vote: schemas.Vote,
              db: Session = Depends(database.get_db),
              current_user=Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(
        models.Post.post_id == vote.post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id : {vote.post_id} not found")

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id,
                                              models.Vote.user_id == current_user.user_id)

    found_vote = vote_query.first()
    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"you have already voted on post {vote.post_id}")
        new_vote = models.Vote(post_id=vote.post_id,
                               user_id=current_user.user_id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully added vote"}
    elif (vote.dir == 0):
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail=f"vote not found")

        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Successfully deleted vote"}

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail = f"dir can only be 0 or 1 but got {vote.dir}")