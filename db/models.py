from datetime import datetime, date

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
    name : str

class ScheduleDoctor(BaseModel):
    user_doctor : str
    schedule : list[list]
    date_ : date

class UserDoctor(User):
    speciality : str

class Doctor(BaseModel):
    user : str
    speciality : str
    name : str

class Dating(BaseModel):
    date_ : date
    doctor : str
    time : str
    patient : str