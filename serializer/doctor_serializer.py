def doctor_serializer(doctors: dict) -> list:
    data = []
    for i in doctors:
        i.pop("_id")
        data.append(i)

    return data

def doctor_schedule_serializer(schedulers : dict):
    data = []
    for i in schedulers:
        i.pop("_id")
        data.append(i)

    return data