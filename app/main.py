from fastapi import FastAPI, Response, status, HTTPException, Depends
import uvicorn
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from app import models, schemas
from app.database import engine, get_db
from sqlalchemy.orm import Session
from typing import List

#  This line is going to create our models
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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

@app.get("/posts", response_model=schemas.PostResponse)
def get_posts(db: Session = Depends(get_db)):
    # Query to get all content of Post model (table)
    posts = db.query(models.Post).all()     
    return posts

@app.get("/posts/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostResponse)
def get_individual_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} not found.")
    return post

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=List[schemas.PostResponse])
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())  #unpacking values
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

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

@app.put("/posts/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.PostResponse)
def change_existing_post(id: int, post: schemas.PostUpdate, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)     #simple SQL query
    post_to_update = post_query.first()     #Post to update
    # checking if the post to update doesn't exist raise a 404 error
    if post_to_update == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id '{id}' does not exist")
    else:
        post_query.update(post.dict(), synchronize_session=False)       #Just to update
        db.commit()

        return post_query.first()


# for debugging
if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8081)