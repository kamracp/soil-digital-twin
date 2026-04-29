def decision(moisture, temp, ph, rain_forecast):

    if rain_forecast:
        irrigation = "DELAY (Rain Expected)"

    elif moisture < 25:
        irrigation = "ON"

    elif moisture > 45:
        irrigation = "OFF"

    else:
        irrigation = "WAIT"

    if ph > 7.5:
        crop = "Wheat / Cotton"
    else:
        crop = "Rice / Potato"

    energy = "Saving due to rain prediction" if rain_forecast else "Normal operation"

    return irrigation, crop, energy