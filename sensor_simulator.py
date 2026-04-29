import random
import time

def get_data():
    moisture = random.randint(20, 60)
    temp = random.randint(25, 40)
    ph = round(random.uniform(6.0, 8.5), 2)
    return moisture, temp, ph