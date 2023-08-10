from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import uvicorn
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from app import models
from app.database import engine, get_db
from sqlalchemy.orm import Session
from app.database import get_db

#  This line is going to create our models
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: Optional[bool] = True

# Implementing loop to not create the server if connetion is not successful.
while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='umairzafar2406', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was Successful!")
        break
    except Exception as error:
        print("Connecting to DB failed")
        print("Error: ", error)
        time.sleep(2)

@app.get("/")
async def root():
    return {"message": "Welcome to my API folks"}

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # Query to get all content of Post model (table)
    posts = db.query(models.Post).all()     
    return {"Posts": posts}

@app.get("/posts/{id}", status_code=status.HTTP_200_OK)
def get_individual_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} not found.")
    return {"data": post}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())  #unpacking values
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {"data": new_post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_individual_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id '{id}' does not exist")
    else:
        post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", status_code=status.HTTP_202_ACCEPTED)
def change_existing_post(id: int, post: Post, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_to_delete = post_query.first()
    if post_to_delete == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id '{id}' does not exist")
    else:
        post_query.update(post.dict(), synchronize_session=False)
        db.commit()

        return {'message': post_query.first()}


# for debugging
if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8081)