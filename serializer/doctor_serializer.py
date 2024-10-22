def doctor_serializer(doctors: dict) -> list:
    data = []
    for i in doctors:
        i.pop("_id")
        data.append(i)

    return data