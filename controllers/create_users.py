import bcrypt
from fastapi import APIRouter, Depends, Form, HTTPException
from auth.dependencies import is_admin
from db.db import user_db
from db.models import User

create_users_route = APIRouter()

@create_users_route.post("/admin/user/create")
async def create_user(user_client : User, current_user : dict = Depends(is_admin)):
    user_on_db = user_db.find_one({"usuario" : user_client.user})
    hashed = bcrypt.hashpw(user_client.password.encode(), bcrypt.gensalt())
    user_client.password = hashed
    if user_on_db:
        raise HTTPException(status_code=400, detail="Usuario duplicado")

    user_db.insert_one(user_client.__dict__)

    return {"Exito" : "Usuario agregado correctamente"}