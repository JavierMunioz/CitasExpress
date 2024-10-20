import string
import random
from datetime import datetime, timedelta
import bcrypt
from fastapi import HTTPException, Form, APIRouter
from db.db import user_db, password_changued_db
from utilities import send_email
from db.models import PasswordChanged

route_password_chagued = APIRouter()

def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

@route_password_chagued.post("/code_verification")
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


    send_email("javidavi16dd@gmail.com", user_on_db["email"], "Verification code citas express", f"Tu codigo para poder cambair la contraseña es: {code}")

    return {"Exito" : f"tu codigo fue enviado al correo {user_on_db['email']}"}

@route_password_chagued.post("/changed_password")
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

    return {"Exito" : "Contraseña cambiada"}
