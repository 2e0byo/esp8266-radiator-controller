radiator_schedule = [
    {"days": ["mon", "tue", "wed", "thu", "fri"], "on": (8, 30), "off": (9, 30)},
    {"days": ["sat", "sun"], "on": (9, 30), "off": (10, 30)},
    {
        "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        "on": (23, 20),
        "off": (0, 0),
    },
]

thermostat_schedule = [
    {
        "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        "on": (22, 00),
        "off": (9, 30),
        "setpoint": 20,
    },
]
