import random
import string
from datetime import datetime, timedelta
import bcrypt
from fastapi import APIRouter, Depends, Form, HTTPException
from auth.dependencies import is_admin
from auth.generate_password import generate_password
from db.db import user_db, password_changued_db
from db.models import User, PasswordChanged
from utilities import send_email, send_code

user_controller = APIRouter()

@user_controller.post("/admin/user/create")
async def create_user(user_client : User, current_user : dict = Depends(is_admin)):
    if user_client.user == "" or user_client.rol == "" or user_client.name == "" or user_client.email == "" or user_client.password == "":
        raise HTTPException(status_code=400, detail="Asegurate de mandar todos los datos")
    user_on_db = user_db.find_one({"user" : user_client.user})
    hashed = bcrypt.hashpw(generate_password().encode(), bcrypt.gensalt())
    user_client.password = hashed
    if user_on_db:
        raise HTTPException(status_code=400, detail="Usuario duplicado")
    user_client.registered = False
    user_db.insert_one(user_client.__dict__)

    return {"Exito" : "Usuario agregado correctamente"}



def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

@user_controller.post("/user/code_verification")
async def requests_code(user_client : str = Form(...)):

    user_on_db = user_db.find_one({'user': user_client})
    on_db = password_changued_db.find_one({'user' : user_client})

    if not user_on_db:
        raise HTTPException(status_code=400, detail="No estas en nuestra Base de Datos.")

    code = generate_verification_code()
    new_on_db = PasswordChanged(
        user=user_on_db["user"],
        verification_code=code,
        date_created=datetime.utcnow()  # O cualquier otra fecha
    )
    if not on_db:
        password_changued_db.insert_one(new_on_db.__dict__)
    else:
        password_changued_db.update_one({"user": user_client}, {"$set": {'verification_code': code, 'date_created' : datetime.utcnow()}})


    send_code("javidavi16dd@gmail.com", user_on_db["email"], "Verification code citas express", code)

    return {"Exito" : f"tu codigo fue enviado al correo {user_on_db['email']}"}

@user_controller.post("/user/changed_password")
async def changed_password(user : str = Form(...), new_password : str = Form(...), code : str = Form(...)):
    user_on_db = user_db.find_one({'user': user})
    on_db = password_changued_db.find_one({'user': user})

    if not user_on_db or not on_db:
        raise HTTPException(status_code=400, detail="Usuario no existente.")

    if not on_db["verification_code"] == code:
        raise HTTPException(status_code=400, detail="Codigo incorrecto")

    if not datetime.utcnow() - on_db["date_created"] < timedelta(minutes=5):
        raise HTTPException(status_code=400, detail="Codigo expirado.")

    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
    user_db.update_one({"user": user}, {"$set": {'password': hashed}})

    password_changued_db.delete_one({"user":user})

    return {"Exito" : "Contraseña cambiada"}
