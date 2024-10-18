def user_serializer(users: dict) -> list:
    data = []
    for i in users:
        i.pop("_id")
        data.append(i)

    return data