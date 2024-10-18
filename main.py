
from fastapi import Depends, FastAPI, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from db.db import usuarios
from auth.auth import get_current_user, create_access_token
from auth.generate_password import generar_contraseña
from utilities import enviar_correo
import bcrypt
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()



app = FastAPI()



@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):

    user = usuarios.find_one({'usuario':f'{form_data.username}'})
    if not user or not bcrypt.checkpw(form_data.password.encode(), user['contrasenna']):  # Implementa hashing en producción
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")
    access_token = create_access_token(data={"sub": user["correo"], "rol": user["rol"], "user" : user["usuario"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    return current_user

@app.post("/user/register")
async def register(usuario : str = Form(...)):
    user = usuarios.find_one({"usuario" : usuario})

    if not user:
        raise HTTPException(status_code=400, detail="No perteneces a esta EPS.")

    if user["registrado"]:
        raise  HTTPException(status_code=400, detail=f"Ya estas registrado revisa tu correo: {user["correo"]}.")
    temp_pass = generar_contraseña()
    enviar_correo("javidavi16dd@gmail.com", user["correo"], "Contraseña temporal citas express", f"Usa: \n{temp_pass}\npara ingresar al sistema.")
    hashed = bcrypt.hashpw(temp_pass.encode(), bcrypt.gensalt())
    update_user = usuarios.update_one({"usuario": usuario}, {"$set": {'contrasenna': hashed, 'registrado' : True}})

    return {"Exito" : f"Se envio al correo:  {user["correo"]} tu nueva contraseña"}
