from random import randint


def create_otp() -> str:
    return str(randint(100000, 999999))
