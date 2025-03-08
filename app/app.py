import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
import uuid
import json
from typing import Dict
from contextlib import asynccontextmanager

from database import (
    setup_database,
    get_user_by_username,
    get_user_by_id,
    create_session,
    get_session,
    delete_session,
)

# TODO: 1. create your own user
INIT_USERS = [
    ("Carlos", "Guerrero", "c5guerrero@ucsd.edu", "CarlosG", "admin", "San Diego", "CA", "USA")
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for managing application startup and shutdown.
    Handles database setup and cleanup in a more structured way.
    """
    # Startup: Setup resources
    try:
        await setup_database(INIT_USERS)  # Make sure setup_database is async
        print("Database setup completed")
        yield
    finally:
        print("Shutdown completed")


# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)


# Static file helpers
def read_html(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()


def get_error_html(username: str) -> str:
    error_html = read_html("./static/error.html")
    return error_html.replace("{username}", username)


@app.get("/")
async def root():
    """Redirect users to /login"""
    # TODO: 2. Implement this route
    return RedirectResponse("/login", 307)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Show login if not logged in, or redirect to profile page"""
    # TODO: 3. check if sessionId is in attached cookies and validate it
    # if all valid, redirect to /user/{username}
    # if not, show login page
    session_id = request.cookies.get("sessionId")
    if session_id:
        session = await get_session(session_id)
        if session:
            user = await get_user_by_id(session["user_id"])
    # Check if session username matches URL username
            if user['username']:
                return RedirectResponse(f"/user/{user['username']}", status_code=302)
    return read_html("./static/login.html")
    

@app.post("/login")
async def login(request: Request):
    """Validate credentials and create a new session if valid"""
    # TODO: 4. Get username and password from form data

    # TODO: 5. Check if username exists and password matches

    # TODO: 6. Create a new session

    # TODO: 7. Create response with:
    #   - redirect to /user/{username}
    #   - set cookie with session ID
    #   - return the response

    data = await request.form();
    username = data.get("username")
    password = data.get("password")

    print(username)
    print(password)

    userInfo = await get_user_by_username(username)

    if userInfo == None:
        print(userInfo)
        return RedirectResponse("/login")
    
    dataUser = userInfo['username']
    dataPass = userInfo['password']

    if (dataUser == username) and (dataPass == password):
        uniqueId = str(uuid.uuid4())
        print(uniqueId);
        print("here5")
        await create_session(userInfo['id'], uniqueId)
        response = RedirectResponse(f"/user/{username}", status_code=302)
        response.set_cookie(key='sessionId',value=uniqueId)
        return response
    else:
        return RedirectResponse("/login")
    


@app.post("/logout")
async def logout(request: Request):
    """Clear session and redirect to login page"""
    # TODO: 8. Create redirect response to /login

    # TODO: 9. Delete sessionId cookie
    session_id = request.cookies.get("sessionId")
    # TODO: 10. Return response
    await delete_session(session_id)
    response = RedirectResponse("/login", status_code=302)

    response.delete_cookie(key="sessionId")

    return response


@app.get("/user/{username}", response_class=HTMLResponse)
async def user_page(username: str, request: Request):
    """Show user profile if authenticated, error if not"""
    # TODO: 11. Get sessionId from cookies

    # TODO: 12. Check if sessionId exists and is valid
    #   - if not, redirect to /login

    # TODO: 13. Check if session username matches URL username
    #   - if not, return error page using get_error_html with 403 status

    # TODO: 14. If all valid, show profile page
    # Get sessionId from cookies

    print("here2")

    session_id = request.cookies.get("sessionId")

    print("here")

    # Check if sessionId exists and is valid
    if not session_id:
        return RedirectResponse("/login")
    
    session = await get_session(session_id)

    if not session:
        return RedirectResponse("/login")
    
    user = await get_user_by_id(session["user_id"])

    print(user["username"])

    # Check if session username matches URL username
    if user['username'] != username:
        return HTMLResponse(get_error_html(username), status_code=403)

    # If all valid, show profile page
    return HTMLResponse(read_html("./static/profile.html").replace("{username}", username))


if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=8000, reload=True)
