from main import get_current_user
from fastapi import Depends, HTTPException

# Verifica si un usuario logueado tiene permisos de administrador
def is_admin(user_client: dict = Depends(get_current_user)):
    if user_client["rol"] != '0':
        raise HTTPException(status_code=400, detail="No eres administrador")
    return user_client
