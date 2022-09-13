import datetime
from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from data_db import data
from typing import Optional

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

    def __post__init__(self):
        self.id += 1


@app.get("/")
def root():
    return {"message": "Ni Han Go!"}


@app.post("/posts")
def get_posts():
    return data


@app.post("/createposts")
def create_posts(post: Post):
    data.append(post)
    print(data)
    return {"message": "successfully created post",
            "data": {
                "title": post.title,
                "date": datetime.datetime.now()
                }               
                
            }
