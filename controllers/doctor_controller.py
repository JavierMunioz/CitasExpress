from datetime import date
import bcrypt
from fastapi import APIRouter, Depends, Form, HTTPException, Query
from auth.dependencies import is_admin
from auth.generate_password import generate_password
from db.db import doctor_schedule_db, user_db, doctors_db
from db.models import Doctor, User, UserDoctor
from serializer.doctor_serializer import doctor_serializer

doctor_controller = APIRouter()

@doctor_controller.post("/admin/doctor/schedule")
async def create_schedule_doctor(doctors_id : str = Form(...), date_ : date = Form(...), current_user : dict = Depends(is_admin)):


    user_on_db = user_db.find_one({"user" : doctors_id, "rol" : "2"})
    if not user_on_db:
        raise HTTPException(status_code=400 ,detail="Asegurate de que todos los ids sean de doctores")

    schedule_on_db = doctor_schedule_db.find_one({"user_doctor" : doctors_id, "date_" : date_.isoformat()})

    if schedule_on_db:
        raise HTTPException(status_code=400, detail="Ya tiene horario asignado para esta fecha")

    schedule_client = {"user_doctor" : doctors_id,
                       "schedule":[["8:00 - 8:30", False],
                                   ["9:00 - 9:30", False],
                                   ["10:00 - 10:30", False],
                                   ["11:00 - 11:30", False],
                                   ["2:00 - 2:30", False],
                                   ["3:00 - 3:30", False],
                                   ["4:00 - 4:30", False],
                                   ["5:00 - 5:30", False]] ,
                       "date_":date_.isoformat()}

    doctor_schedule_db.insert_one(schedule_client)

    return {"Exito" : "Horarios creados correctamente"}

@doctor_controller.post("/admin/doctor/speciality")
async def doctor_speciality(doctors_speciality : str = Form(...), current_user : dict = Depends(is_admin)):
    # 0 - Laboratorio, 1 - Pediatra, 3 - Medicina General
    doctors_on_db = doctors_db.find({"speciality" : doctors_speciality})

    return doctor_serializer(doctors_on_db)

@doctor_controller.post('/admin/doctor/create')
async def doctor_create(user_client : UserDoctor, current_user : dict = Depends(is_admin)):
    if user_client.user == "" or user_client.rol == "" or user_client.name == "" or user_client.email == "" or user_client.password == "":
        raise HTTPException(status_code=400, detail="Asegurate de mandar todos los datos")
    user_on_db =  user_db.find_one({"user" : user_client.user})

    if user_on_db:
        raise  HTTPException(status_code=400, detail="Usuario Duplicado")

    if user_client.rol != "2":
        raise HTTPException(status_code=400, detail="Asegurate de querer guardar un doctor")

    doctor_client = Doctor(user=user_client.user, name=user_client.name, speciality=user_client.speciality)
    user_client.password = bcrypt.hashpw(generate_password().encode(), bcrypt.gensalt())
    user_client = User(user=user_client.user, password=user_client.password, name=user_client.name, rol=user_client.rol, email=user_client.email, registered=user_client.registered)
    user_client.registered = False
    user_db.insert_one(user_client.__dict__)
    doctors_db.insert_one(doctor_client.__dict__)

    return {"Exito" :  "Doctor creado correctamente"}

@doctor_controller.get("/admin/doctor/schedule/list")
async def doctor_schedule_list(doctors_id : str = Query(...), date_ : date = Query(...), current_user : dict = Depends(is_admin)):

    doctor_on_db = user_db.find_one({"user" : doctors_id, "rol" : "2"})

    if not doctor_on_db:
        raise HTTPException(status_code=400, detail="No es un doctor")

    doctor_schedule_on_db = doctor_schedule_db.find_one({"user_doctor" : doctors_id, "date_" : date_.isoformat()})
    doctor_schedule_on_db.pop("_id")
    return doctor_schedule_on_db