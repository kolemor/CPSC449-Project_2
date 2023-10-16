import contextlib
import sqlite3

from typing import List
from fastapi import Depends, HTTPException, APIRouter, status
from schemas import User_info, Register

router = APIRouter()

database = "users.db"

# Connect to the database
def get_db():
    with contextlib.closing(sqlite3.connect(database, check_same_thread=False)) as db:
        db.row_factory = sqlite3.Row
        yield db

#A simple test endpoint to list out all the users and their relevant info
@router.get("/users", response_model=List[User_info], tags=['Users'])
def get_all_users(db: sqlite3.Connection = Depends(get_db)):
    users_info = []

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT * FROM users
        """
    )
    users_data = cursor.fetchall()

    if not users_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")

    for user in users_data:
        cursor.execute(
            """
            SELECT role FROM role WHERE user_id = ?
            """,
            (user["uid"],)
        )
        roles_data = cursor.fetchall()
        roles = [role["role"] for role in roles_data]

        user_information = User_info(
            uid=user["uid"],
            name=user["name"],
            password=user["password"],
            roles=roles  # Using a list of strings for roles
        )

        users_info.append(user_information)

    return users_info

@router.get("/users/login", tags=['Users'])
def get_user_login(db: sqlite3.Connection = Depends(get_db)):
    #TODO 
    # login enpoint implementation
    cursor = db.cursor()

@router.post("/users/register", tags=['Users'])
def get_user_login(register_data: Register, db: sqlite3.Connection = Depends(get_db)):
    #TODO 
    # register enpoint implementation
    cursor = db.cursor()

@router.get("/users/{uid}/password", tags=['Users'])
def get_user_login(db: sqlite3.Connection = Depends(get_db)):
    #TODO 
    # /check user password enpoint implementation
    cursor = db.cursor()