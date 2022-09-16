import datetime
import psycopg2
import time

from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Response, HTTPException, status
from pydantic import BaseModel
from data_db import data
from typing import Optional
from random import randrange
from dotenv import dotenv_values

app = FastAPI()

SLEEP_TIME = 2

while True:
    try:
        config = dotenv_values(".env")
        host = config["HOST"]
        database = config["DATABASE"]
        user = config["USER"]
        password = config["PASSWORD"]
        database_connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            cursor_factory=RealDictCursor)
        cursor = database_connection.cursor()
        print("[+] Database connection established")
        break
    except Exception as err:
        print(f"[-] Error: {err}")
        time.sleep(SLEEP_TIME)

class Post(BaseModel):
    title: str
    content: str
    published: bool = True


def search_post_by_id(id: int):
    if id == -1:
        return data[-1]
    else:
        for post in data:
            if post["id"] == id:
                return post


def find_post_index(id: int):
    for i, post in enumerate(data):
        if post["id"] == id:
            return i
    return None


@app.get("/posts")
def get_posts(response: Response):
    response.status_code = status.HTTP_200_OK
    return data


@app.get("/posts/{id}")
def get_post_by_id(id: int, response: Response):
    return_data = search_post_by_id(id)
    if not return_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")
    return {"message": return_data}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, response: Response):
    submitted_data = post.dict()
    id = randrange(4, 10000000)
    submitted_data["id"] = id
    data.append(submitted_data)

    return {
        "message": "successfully created post",
        "data":
            {
                "title": post.title,
                "post-id": id,
                "date": datetime.datetime.now()
            }
    }


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_post_index(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")
    data.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_entire_post(id: int, post: Post):
    index = find_post_index(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")
    updated_data = post.dict()
    updated_data["id"] = id
    data.append(updated_data)
    return {
        "message": f"successfully updated post: {id}",
        "data":
            {
                "title": post.title,
                "post-id": id,
                "date": datetime.datetime.now()
            }
    }
