from fastapi import Depends, FastAPI, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from auth.auth import get_current_user, create_access_token
from auth.generate_password import generar_contraseña
from utilities import enviar_correo
import bcrypt
from dotenv import load_dotenv
import os
from db.db import usuarios
from serializer.user_serializer import user_serializer
from controllers.password_changued import route_password_chagued

# Cargar las variables del archivo .env
load_dotenv()

app = FastAPI()
app.include_router(route_password_chagued)
# Endpoint retorna el token de usuario si sus credenciales son correctas
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = usuarios.find_one({'usuario': form_data.username})
    if not user or not bcrypt.checkpw(form_data.password.encode(), user['contrasenna']):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    access_token = create_access_token(data={"sub": user["correo"], "rol": user["rol"], "user": user["usuario"]})
    return {"access_token": access_token, "token_type": "bearer"}

# Retorna el usuario actual
@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

# Permite registrarse al usuario
@app.post("/user/register")
async def register(usuario: str = Form(...)):
    user = usuarios.find_one({"usuario": usuario})

    if not user:
        raise HTTPException(status_code=400, detail="No perteneces a esta EPS.")

    if user["registrado"]:
        raise HTTPException(status_code=400, detail=f"Ya estás registrado, revisa tu correo: {user['correo']}.")

    temp_pass = generar_contraseña()
    enviar_correo("javidavi16dd@gmail.com", user["correo"], "Contraseña temporal citas express",
                  f"Usa: \n{temp_pass}\npara ingresar al sistema.")

    hashed = bcrypt.hashpw(temp_pass.encode(), bcrypt.gensalt())
    usuarios.update_one({"usuario": usuario}, {"$set": {'contrasenna': hashed, 'registrado': True}})

    return {"Éxito": f"Se envió al correo: {user['correo']} tu nueva contraseña."}

# Verifica si un usuario logueado tiene permisos de administrador
def is_admin(user: dict = Depends(get_current_user)):
    if user["rol"] != '0':
        raise HTTPException(status_code=400, detail="No eres administrador")
    return user

# Retorna los usuarios registrados siempre y cuando los el usuario este como admin
@app.get("/dashboard/admin")
async def usuarios_on_db(current_user: dict = Depends(is_admin)):
    return user_serializer(usuarios.find())

