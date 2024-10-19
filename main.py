from fastapi import Depends, FastAPI, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from auth.auth import get_current_user, create_access_token
from auth.generate_password import generate_password
from utilities import send_email
import bcrypt
from dotenv import load_dotenv
import os
from db.db import user_db
from serializer.user_serializer import user_serializer
from controllers.password_changued import route_password_chagued

# Cargar las variables del archivo .env
load_dotenv()

app = FastAPI()
app.include_router(route_password_chagued)
# Endpoint retorna el token de usuario si sus credenciales son correctas
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_on_db = user_db.find_one({'usuario': form_data.username})
    if not user_on_db or not bcrypt.checkpw(form_data.password.encode(), user_on_db['contrasenna']):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    access_token = create_access_token(data={"sub": user_on_db["correo"], "rol": user_on_db["rol"], "user": user_on_db["usuario"]})
    return {"access_token": access_token, "token_type": "bearer"}

# Retorna el usuario actual
@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

# Permite registrarse al usuario
@app.post("/user/register")
async def register(user_client: str = Form(...)):
    user_on_db = user_db.find_one({"usuario": user_client})

    if not user_on_db:
        raise HTTPException(status_code=400, detail="No perteneces a esta EPS.")

    if user_on_db["registrado"]:
        raise HTTPException(status_code=400, detail=f"Ya estás registrado, revisa tu correo: {user_on_db['correo']}.")

    temp_pass = generate_password()
    send_email("javidavi16dd@gmail.com", user_on_db["correo"], "Contraseña temporal citas express",
                  f"Usa: \n{temp_pass}\npara ingresar al sistema.")

    hashed = bcrypt.hashpw(temp_pass.encode(), bcrypt.gensalt())
    user_db.update_one({"usuario": user_client}, {"$set": {'contrasenna': hashed, 'registrado': True}})

    return {"Éxito": f"Se envió al correo: {user_on_db['correo']} tu nueva contraseña."}

# Verifica si un usuario logueado tiene permisos de administrador
def is_admin(user_client: dict = Depends(get_current_user)):
    if user_client["rol"] != '0':
        raise HTTPException(status_code=400, detail="No eres administrador")
    return user_client

# Retorna los usuarios registrados siempre y cuando los el usuario este como admin
@app.get("/dashboard/admin")
async def usuarios_on_db(current_user: dict = Depends(is_admin)):
    return user_serializer(user_db.find())

