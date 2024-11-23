import random


def generate_random_otp(length=6):
    otp = "".join([str(random.randint(0, 9)) for _ in range(length)])
    return otp
