from pydantic import BaseModel
from typing import List

class User_info(BaseModel):
    uid: int
    name: str
    password: str
    roles: List

class User(BaseModel):
    name: str
    password: str