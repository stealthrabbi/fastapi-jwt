from fastapi import FastAPI, Body, Depends, Response, status

from app.model import PostSchema, UserSchema, UserLoginSchema
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import signJWT, decodeJWT


posts = [
    {
        "id": 1,
        "title": "Pancake",
        "content": "Lorem Ipsum ..."
    }
]

users = []

app = FastAPI()


# helpers

def check_user(data: UserLoginSchema):
    # MPF TODO - this is is using a list of users in RAM -- should use LDAP
    # THis is where we'd make a call to LDAP to authenticate
    # We should only log in on the login call. On all other API calls, we 
    # add a dependency on the JWT Bearer, and we check the token for validity / expiration
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False

async def get_current_user(token: str = Depends(JWTBearer())):
    user = decodeJWT(token)
    print("user: " + str(user))
    return user

# route handlers

@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your blog!."}


@app.get("/posts", tags=["posts"])
async def get_posts() -> dict:
    return { "data": posts }


@app.get("/posts/{id}", tags=["posts"])
async def get_single_post(id: int) -> dict:
    if id > len(posts):
        return {
            "error": "No such post with the supplied ID."
        }

    for post in posts:
        if post["id"] == id:
            return {
                "data": post
            }


# @app.post("/posts", dependencies=[Depends(JWTBearer())], tags=["posts"])
# MPF - changed this to include the current user, so that the user ID can be known / printed
# this can be expanded for like "Get current user with role X". That function would return None
# if the current user doesn't have that role.
@app.post("/posts", tags=["posts"])
async def add_post(post: PostSchema, current_user = Depends(get_current_user)) -> dict:
    print("making a post for user: " + str(current_user))
    post.id = len(posts) + 1
    posts.append(post.dict())
    return {
        "data": "post added."
    }


@app.post("/user/signup", tags=["user"])
async def create_user(user: UserSchema = Body(...)):
    users.append(user) # replace with db call, making sure to hash the password first
    return signJWT(user.email)


@app.post("/user/login", tags=["user"])
async def user_login(response: Response, user: UserLoginSchema = Body(...)):
    if check_user(user):
        return signJWT(user.email)
        # MPF I added this change here for setting 403 check
    response.status_code = status.HTTP_403_FORBIDDEN
    return {
        "error": "Wrong login details!"
    }

@app.get("/users/me", tags=["user"])
async def get_me_user(response: Response, current_user = Depends(get_current_user)):
    return current_user


