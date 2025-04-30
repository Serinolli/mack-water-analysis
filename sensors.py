import random

def get_fake_ph():
    return round(random.uniform(6.5, 8.5), 2)

def get_fake_turbidity():
    return round(random.uniform(0, 300), 1)

def get_fake_temperature():
    return round(random.uniform(22, 28), 1)