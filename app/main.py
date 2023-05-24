from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    # id: int
    # published: Optional[bool] = True
    # rating: Optional[int] = None

class UpdatePost(BaseModel):
    title: str
    content: str

my_posts = [
    {"title": "This is the title 1", "content": "This is content 1", "id": 1},
    {"title": "This is the title 2", "content": "This is content 2", "id": 2}
            ]

def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post


@app.get("/")
async def root():
    return {"message": "Welcome to my API folks"}


@app.get("/posts")
def get_posts():
    return my_posts


@app.get("/posts/{id}", status_code=status.HTTP_200_OK)
def get_individual_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} not found.")
    return {"data": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 10000000)
    my_posts.append(post_dict)
    print(my_posts)
    return {"data": post_dict}


def get_index_to_remove_post(id):
    for index, post in enumerate(my_posts):
        if post['id'] == id:
            return index


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_individual_post(id: int):
    index = get_index_to_remove_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id '{id}' does not exist")
    my_posts.pop(index)
    print(my_posts)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", status_code=status.HTTP_202_ACCEPTED)
def change_existing_post(id: int, update_post: UpdatePost):
    updated_post_dict = update_post.dict()
    index = get_index_to_remove_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id '{id}' does not exist")
    else:
        my_posts[index] = updated_post_dict
        return {'message': 'Updated the Post'}


@app.get("/posts/latest", status_code=status.HTTP_200_OK)
def latest_post():
    return my_posts[len(my_posts)-1]

