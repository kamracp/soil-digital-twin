def energy_calc(pump_kw, hours_run, tariff, optimized_hours):

    # Base case
    energy_base = pump_kw * hours_run
    cost_base = energy_base * tariff

    # Optimized case
    energy_opt = pump_kw * optimized_hours
    cost_opt = energy_opt * tariff

    saving_kwh = energy_base - energy_opt
    saving_rs = cost_base - cost_opt

    if cost_base > 0:
        saving_percent = (saving_rs / cost_base) * 100
    else:
        saving_percent = 0

    return {
        "base_cost": round(cost_base, 2),
        "opt_cost": round(cost_opt, 2),
        "saving_rs": round(saving_rs, 2),
        "saving_percent": round(saving_percent, 2)
    }