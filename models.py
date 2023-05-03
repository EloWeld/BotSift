from typing import Optional
from pydantic import BaseModel

from config import MDB

class TgUser(BaseModel):
    user_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    
    def create(self):
        MDB.Users.insert_one(self.dict())
