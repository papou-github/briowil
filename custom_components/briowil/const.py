"""Controller protocol constants and mapping between native color/program numbers and Home Assistant."""

DOMAIN = "briowil"

CONF_SERVER_IP = "server_ip"
CONF_REFRESH_INTERVAL = "refresh_interval"

DEFAULT_PORT = 30302

DEFAULT_REFRESH_INTERVAL = 10

MIN_REFRESH_INTERVAL = 1
MAX_REFRESH_INTERVAL = 300


SOLID_COLOR_MAP = {
    "Warm White": 0,
    "White": 1,
    "Blue": 2,
    "Lagoon": 3,
    "Cyan": 4,
    "Purple": 5,
    "Magenta": 6,
    "Pink": 7,
    "Red": 8,
    "Orange": 9,
    "Green": 10,
}


EFFECT_MAP = {
    "Gradient": 16,
    "Rainbow": 17,
    "Parade": 18,
    "Techno": 19,
    "Horizon": 20,
    "Hazard": 21,
    "Magical": 22,
}


COLOR_NUMBER_TO_NAME = {
    value: key
    for key, value in {
        **SOLID_COLOR_MAP,
        **EFFECT_MAP,
    }.items()
}


HS_COLOR_MAP = {
    0: (40, 35),
    1: (0, 0),
    2: (240, 100),
    3: (200, 100),
    4: (180, 100),
    5: (270, 100),
    6: (300, 100),
    7: (330, 80),
    8: (0, 100),
    9: (30, 100),
    10: (120, 100),
}


BRIGHTNESS_MAP = {
    0: 64,
    1: 128,
    2: 191,
    3: 255,
}

EFFECT_SPEED_MAP = {
    "Slow": 0,
    "Medium": 1,
    "Fast": 2,
}


EFFECT_SPEED_NUMBER_TO_NAME = {
    value: key
    for key, value in EFFECT_SPEED_MAP.items()
}