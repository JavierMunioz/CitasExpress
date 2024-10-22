from datetime import date
from fastapi import APIRouter, Depends, Form, HTTPException
from auth.dependencies import is_admin
from db.db import doctor_schedule_db, user_db

create_schedule_route = APIRouter()

@create_schedule_route.post("/admin/doctor/schedule")
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