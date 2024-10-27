from datetime import date
from fastapi import APIRouter, Depends, HTTPException,  Query
from db.db import user_db, assigned_dating_db,doctor_schedule_db, dating_db
from db.models import Dating, AssignedDating
from main import is_admin


dating_controller = APIRouter()

@dating_controller.post("/admin/dating/create")
async def dating_create(dating_client : Dating , current_user : dict = Depends(is_admin)):

    doctor_on_db =  user_db.find_one({"user" : dating_client.doctor, "rol" : "2"})

    if not doctor_on_db:
        raise HTTPException(status_code=400, detail="Debe ser un doctor")

    doctor_schedule =  doctor_schedule_db.find_one({"user_doctor" : doctor_on_db.get("user") , "date_" : dating_client.date_.isoformat()})

    if not doctor_schedule:
        raise HTTPException(status_code=400, detail="El doctor no tiene horario asignado para esta fecha")


    doctor_schedule.pop("_id")

    schedule = doctor_schedule.get("schedule", [])
    available_slot = None
    for slot in schedule:
        if slot[0] == dating_client.time and not slot[1]:  # Si coincide el horario y no está ocupado
            available_slot = slot
            break

    if not available_slot:
        raise HTTPException(status_code=400, detail="Este horario ya está ocupado o no es válido")

    dating_client.date_ = dating_client.date_.isoformat()
    dating_db.insert_one(dating_client.__dict__)

    available_slot[1] = True
    doctor_schedule_db.update_one(
        {"user_doctor": doctor_on_db.get("user"), "date_": dating_client.date_},
        {"$set": {"schedule": schedule}}
    )


    return {"Exito" : "Cita creada correctamente"}


@dating_controller.get("/admin/dating/list-filter")
async def dating_list_filter(date_ : date = Query(...), speciality : str = Query(...), doctor_ : str =  Query(...)):
    data = []
    dating_on_db = dating_db.find({"date_" : date_.isoformat() , "speciality" : speciality, "doctor" : doctor_})

    if not dating_on_db:
        return data

    for i in dating_on_db:
        i.pop("_id")
        occupied = assigned_dating_db.find({"date_": date_.isoformat(), "speciality": speciality, "doctor": doctor_})
        if not occupied:
            data.append(i)
    return data

@dating_controller.post("/admin/assigned_dating")
async def assigned_dating(dating_client : AssignedDating):
    assigned_dating_on_db = assigned_dating_db.find_one({"date_" : dating_client.date_.isoformat(), "time" : dating_client.time, "speciality" : dating_client.speciality, "doctor" : dating_client.doctor})

    if dating_client.time not in  ["8:00 - 8:30",
                                   "9:00 - 9:30",
                                   "10:00 - 10:30",
                                   "11:00 - 11:30",
                                   "2:00 - 2:30",
                                   "3:00 - 3:30",
                                   "4:00 - 4:30",
                                   "5:00 - 5:30",]:
        raise HTTPException(status_code=400, detail="Error de horario")



    if assigned_dating_on_db:
        raise HTTPException(status_code=400, detail="esta cita ya esta ocupada")

    assigned_dating_db.insert_one({
        "date_" : dating_client.date_.isoformat(),
        "doctor" : dating_client.doctor,
        "time" : dating_client.time,
        "speciality" : dating_client.speciality,
        "patient" : dating_client.patient
    })

    return {"Exito" : "Cita asignada correctamente"}


@dating_controller.get("/admin/dating/list")
async def dating_list(current_user = Depends(is_admin)):
    dating_on_db = assigned_dating_db.find()

    data = []

    for i in dating_on_db:
        i.pop("_id")
        data.append(i)

    return data