import contextlib
import sqlite3

from typing import List
from fastapi import Depends, HTTPException, APIRouter, status, Query
from users_schemas import User_info, User
from users_hash import hash_password, verify_password

router = APIRouter()

database = "users.db"

# Connect to the database
def get_db():
    with contextlib.closing(sqlite3.connect(database, check_same_thread=False)) as db:
        db.row_factory = sqlite3.Row
        yield db

#==========================================Users==================================================

@router.post("/users/login", tags=['Users'])
def get_user_login(user: User, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT * FROM users WHERE name = ?
        """, (user.name,)
    )
    user_data = cursor.fetchone()
    
    # Check if user exists
    if not user_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username")

    # Verify the password
    if not verify_password(user.password, user_data['password']):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")
    
    #TODO: JWT validation

    # return message
    return {"message": "Login successful"}

@router.post("/users/register", tags=['Users'])
def register_new_user(user: User, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT * FROM users WHERE name = ?
        """, (user.name,)
    )
    user_data = cursor.fetchone()
    
    # Check if user exists
    if user_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    # Hash the password before storing it
    password_hash = hash_password(user.password)

    #Store new user data in DB
    cursor.execute(
        """
        INSERT INTO users (name, password)
        VALUES (?, ?)
        """, (user.name, password_hash)
    )

    #Give new user default role of 'student'
    cursor.execute(
        """
        SELECT * FROM users WHERE name = ?
        """, (user.name,)
    )
    user_data = cursor.fetchone()

    cursor.execute(
        """
        INSERT INTO user_role (user_id, role_id)
        VALUES (?, ?)
        """, (user_data['uid'], 1)
    )

    db.commit()

    return {"message": "User created successfully"}

@router.get("/users/check_password", tags=['Users'])
def get_user_password(username: str = Query(..., title="Username", description="Your username"),
    password: str = Query(..., title="Password", description="Your password"),
    db: sqlite3.Connection = Depends(get_db)):

    # Query the database to retrieve the user's password hash
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT password FROM users WHERE name = ?
        """, (username,)
    )
    q = cursor.fetchone()

    # Check if user exists
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check the password
    password_hash = q[0]

    if verify_password(password, password_hash):
        return {"message": "Password is correct"}
    else:
        return {"message": "Password is incorrect"}
    

#==========================================Test Endpoints==================================================

# None of the following endpoints are required (I assume), but might be helpful
# for testing purposes

#A simple test endpoint to list out all the users and their relevant info
@router.get("/debug", response_model=List[User_info], tags=['Debug'])
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
            SELECT role FROM user_role 
            JOIN role ON user_role.role_id = role.rid
            JOIN users ON user_role.user_id = users.uid
            WHERE user_id = ?
            """,
            (user["uid"],)
        )
        roles_data = cursor.fetchall()
        roles = [role["role"] for role in roles_data]

        user_information = User_info(
            uid=user["uid"],
            name=user["name"],
            password=user["password"],
            roles=roles
        )

        users_info.append(user_information)

    return users_info

# Get a single users information
@router.get("/debug/{user_id}", response_model=List[User_info], tags=['Debug'])
def get_one_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    users_info = []

# Change a users role
@router.put("/debug/{user_id}", response_model=List[User_info], tags=['Debug'])
def change_role(db: sqlite3.Connection = Depends(get_db)):
    users_info = []