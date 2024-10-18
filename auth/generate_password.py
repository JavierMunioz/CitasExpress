import random
import string


def generar_contraseña(longitud=12):
    if longitud < 8:
        raise ValueError("La longitud de la contraseña debe ser al menos 8 caracteres.")

    # Define los caracteres que se pueden usar
    caracteres = string.ascii_letters + string.digits + string.punctuation

    # Genera la contraseña
    contraseña = ''.join(random.choice(caracteres) for _ in range(longitud))

    return contraseña


