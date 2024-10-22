from fastapi import Depends, FastAPI, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from auth.auth import get_current_user, create_access_token
from auth.generate_password import generate_password
from utilities import send_email
import bcrypt
from dotenv import load_dotenv
from db.db import user_db
from serializer.user_serializer import user_serializer
from auth.dependencies import is_admin
from fastapi.middleware.cors import CORSMiddleware
from controllers.user_controller import user_controller
from controllers.doctor_controller import doctor_controller
from controllers.dating_controller import dating_controller

# Cargar las variables del archivo .env
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_controller)
app.include_router(doctor_controller)
app.include_router(dating_controller)

# Endpoint retorna el token de usuario si sus credenciales son correctas
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_on_db = user_db.find_one({'user': form_data.username})
    if not user_on_db or not bcrypt.checkpw(form_data.password.encode(), user_on_db['password']):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    access_token = create_access_token(data={"sub": user_on_db["email"], "rol": user_on_db["rol"], "user": user_on_db["user"]})
    return {"access_token": access_token, "token_type": "bearer"}

# Retorna el usuario actual
@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

# Permite registrarse al usuario
@app.post("/user/register")
async def register(user_client: str = Form(...)):
    user_on_db = user_db.find_one({"user": user_client})

    if not user_on_db:
        raise HTTPException(status_code=400, detail="No perteneces a esta EPS.")

    if user_on_db["registered"]:
        raise HTTPException(status_code=400, detail=f"Ya estás registrado, revisa tu correo: {user_on_db['email']}.")

    temp_pass = generate_password()
    send_email("javidavi16dd@gmail.com", user_on_db["email"], "Contraseña temporal citas express",
                  f"Usa: \n{temp_pass}\npara ingresar al sistema.")

    hashed = bcrypt.hashpw(temp_pass.encode(), bcrypt.gensalt())
    user_db.update_one({"user": user_client}, {"$set": {'password': hashed, 'registered': True}})

    return {"Éxito": f"Se envió al correo: {user_on_db['email']} tu nueva contraseña."}


# Retorna los usuarios registrados siempre y cuando los el usuario este como admin
@app.get("/admin/user/list")
async def users_on_db(current_user: dict = Depends(is_admin)):
    return user_serializer(user_db.find({"rol":"1"}))

