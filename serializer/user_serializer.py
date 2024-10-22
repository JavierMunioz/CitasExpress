def user_serializer(users: dict) -> list:
    data = []
    for i in users:
        i.pop("_id")
        i.pop("password")
        data.append(i)

    return data