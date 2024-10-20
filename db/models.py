from datetime import datetime

from pydantic import BaseModel

class PasswordChanged(BaseModel):
    user : str
    verification_code : str
    date_created : datetime

class User(BaseModel):
    user : str
    password : str
    rol : str
    email : str
    registered : bool