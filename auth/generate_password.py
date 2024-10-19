import random
import string


def generate_password(lenght=12):
    if lenght < 8:
        raise ValueError("La longitud de la contraseña debe ser al menos 8 caracteres.")


    chars = string.ascii_letters + string.digits + string.punctuation

    chars = ''.join(random.choice(chars) for _ in range(lenght))

    return chars


