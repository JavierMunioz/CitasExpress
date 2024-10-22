from fastapi import APIRouter, Depends, Form, HTTPException
from auth.dependencies import is_admin
from db.db import doctors_db
from serializer.doctor_serializer import doctor_serializer

doctor_speciality_route = APIRouter()

@doctor_speciality_route.post("/admin/doctor/speciality")
async def doctor_speciality(doctors_speciality : str = Form(...), current_user : dict = Depends(is_admin)):
    # 0 - Neurologia, 1 - Pediatra, 3 - Medicina General
    doctors_on_db = doctors_db.find({"speciality" : doctors_speciality})

    return doctor_serializer(doctors_on_db)