from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import uvicorn
import time
import psycopg2
from psycopg2.extras import RealDictCursor

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
def get_posts():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return {"posts": posts}

@app.get("/posts/{id}", status_code=status.HTTP_200_OK)
def get_individual_post(id: int):
    cursor.execute("SELECT * FROM posts WHERE id = %s", (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} not found.")
    return {"data": post}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    # We are not using f-string below as is not safe and can have SQL injection vulenerability.
    cursor.execute("""INSERT INTO posts (title, content)
                    VALUES (%s, %s) RETURNING *""", (post.title, post.content))
    new_post = cursor.fetchone()
    conn.commit()

    return {"data": new_post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_individual_post(id: int):
    cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (str(id)))
    deleted_post = cursor.fetchone()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id '{id}' does not exist")

    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", status_code=status.HTTP_202_ACCEPTED)
def change_existing_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title =%s, content = %s, published = %s
                   WHERE id = %s RETURNING * """, 
                   (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id '{id}' does not exist")
    else:
        conn.commit()
        return {'message': updated_post}


# for debugging
if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8081)