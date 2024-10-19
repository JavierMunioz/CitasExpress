import string
import random
from datetime import datetime, timedelta

import bcrypt
from fastapi import HTTPException, Form, APIRouter
from db.db import usuarios, password_changued
from utilities import enviar_correo
from db.models import PasswordChanged

route_password_chagued = APIRouter()

def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

@route_password_chagued.post("/code_verification")
async def requests_code(usuario : str = Form(...)):

    user = usuarios.find_one({'usuario': usuario})
    on_db = password_changued.find_one({'user' : usuario})

    if not user:
        raise HTTPException(status_code=400, detail="No estas en nuestra Base de Datos.")

    code = generate_verification_code()
    new_on_db = PasswordChanged(
        user=user["usuario"],
        verification_code=code,
        date_created=datetime.utcnow()  # O cualquier otra fecha
    )
    if not on_db:
        password_changued.insert_one(new_on_db.__dict__)
    else:
        password_changued.update_one({"user": usuario}, {"$set": {'verification_code': code, 'date_created' : datetime.utcnow()}})


    enviar_correo("javidavi16dd@gmail.com", user["correo"], "Verification code citas express", f"Tu codigo para poder cambair la contraseña es: {code}")

    return {"Exito" : f"tu codigo fue enviado al correo {user['correo']}"}

@route_password_chagued.post("/changed_password")
async def changed_password(user : str = Form(...), new_password : str = Form(...), code : str = Form(...)):
    user_on_db = usuarios.find_one({'usuario': user})
    on_db = password_changued.find_one({'user': user})

    if not user_on_db or not on_db:
        raise HTTPException(status_code=400, detail="Usuario no existente.")

    if not on_db["verification_code"] == code:
        raise HTTPException(status_code=400, detail="Codigo incorrecto")

    if not datetime.utcnow() - on_db["date_created"] < timedelta(minutes=5):
        raise HTTPException(status_code=400, detail="Codigo expirado.")

    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
    usuarios.update_one({"usuario": user}, {"$set": {'contrasenna': hashed}})

    return {"Exito" : "Contraseña cambiada"}
