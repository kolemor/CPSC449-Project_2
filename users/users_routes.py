import contextlib
import sqlite3
import typing
import collections
import os

from fastapi import Depends, HTTPException, APIRouter, status, Query
from users.users_schemas import *
from users.users_hash import hash_password, verify_password
from users.mkclaims import generate_claims

router = APIRouter()

primary_database = "var/primary/fuse/users.db"
secondary_database = "var/secondary/fuse/users.db"
tertiary_database = "var/tertiary/fuse/users.db"

# Used for the search endpoint
SearchParam = collections.namedtuple("SearchParam", ["name", "operator"])
SEARCH_PARAMS = [
    SearchParam(
        "uid",
        "=",
    ),
    SearchParam(
        "name",
        "LIKE",
    ),
    SearchParam(
        "role",
        "LIKE",
    ),
]

# Flag to track the last database used for read operations
last_read_db = None  # Start with None to use secondary database first

# Connect to the appropriate database based on the endpoint
def get_db_read():
    
    # Database availability check
    available_databases = []

    if os.path.exists(primary_database):
        available_databases.append(primary_database)

    if os.path.exists(secondary_database):
        available_databases.append(secondary_database)

    if os.path.exists(tertiary_database):
        available_databases.append(tertiary_database)

    if not available_databases:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="All databases are unavailable")
    
    else:
        global last_read_db

        if available_databases[1] and available_databases[2]:
            if last_read_db == secondary_database:
                last_read_db = tertiary_database
            else:
                last_read_db = secondary_database
        elif available_databases[1] and not available_databases[2]:
            last_read_db = secondary_database
        elif not available_databases[1] and available_databases[2]:
            last_read_db = tertiary_database
        else:
            last_read_db = primary_database

        with contextlib.closing(sqlite3.connect(last_read_db, check_same_thread=False)) as db:
            db.row_factory = sqlite3.Row
            yield db
    
def get_db_write():
    
    # Database availability check
    available_databases = []

    if os.path.exists(primary_database):
        with contextlib.closing(sqlite3.connect(primary_database, check_same_thread=False)) as db:
            db.row_factory = sqlite3.Row
            yield db
    else:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")


#==========================================Users==================================================

# The login enpoint, where JWT validation needs to occur
@router.post("/users/login", tags=['Users'])
def get_user_login(user: User, db: sqlite3.Connection = Depends(get_db_read)):
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
    
    # Retrieve roles for the student
    cursor.execute(
           """
           SELECT role FROM user_role
           JOIN role ON user_role.role_id = role.rid
           JOIN users ON user_role.user_id = users.uid
           WHERE user_id = ?
           """,
           (user_data["uid"],)
       )
    roles_data = cursor.fetchall()

    roles = [role["role"] for role in roles_data]

    #Issue JWT token
    token_data = generate_claims(user_data['name'], user_data['uid'], roles)
    return token_data



# Create new user endpoint
@router.post("/users/register", tags=['Users'])
def register_new_user(user: User, db: sqlite3.Connection = Depends(get_db_write)):
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


# Have a user check their password
@router.get("/users/check_password", tags=['Users'])
def get_user_password(username: str = Query(..., title="Username", description="Your username"),
    password: str = Query(..., title="Password", description="Your password"),
    db: sqlite3.Connection = Depends(get_db_read)):

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


# Search for specific users based on optional parameters,
# if no parameters are given, returns all users
@router.get("/debug/search", tags=['Debug'])
def search_for_users(uid: typing.Optional[str] = None,
                 name: typing.Optional[str] = None,
                 role: typing.Optional[str] = None,
                 db: sqlite3.Connection = Depends(get_db_read)):
    
    users_info = []

    sql = """SELECT * FROM users
             LEFT JOIN user_role ON users.uid = user_role.user_id
             LEFT JOIN role ON user_role.role_id = role.rid"""
    
    conditions = []
    values = []
    arguments = locals()

    for param in SEARCH_PARAMS:
        if arguments[param.name]:
            if param.operator == "=":
                conditions.append(f"{param.name} = ?")
                values.append(arguments[param.name])
            else:
                conditions.append(f"{param.name} LIKE ?")
                values.append(f"%{arguments[param.name]}%")
    
    if conditions:
        sql += " WHERE "
        sql += " AND ".join(conditions)

    cursor = db.cursor()

    cursor.execute(sql, values)
