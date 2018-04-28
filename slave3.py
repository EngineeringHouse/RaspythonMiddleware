# RPi Pinouts

# I2C Pins
# GPIO2 -> SDA
# GPIO3 -> SCL

# IMPORTS

import json
import urllib.request

# Testing disables some things (so it runs away from raspi)
testMode = False
if not testMode:
    import smbus

    # for RPI version 1, use "bus = smbus.SMBus(0)"
    bus = smbus.SMBus(1)

# RESTful endpoint
base_url = "http://ehmain.rh.rit.edu/api/"


def main():
    try:
        f = open('./room_id.conf', 'r')
        room_id = int(f.readLine().strip())
        f.close()

    except FileNotFoundError as e:
        room_id = 8126

    # Listen for incoming messages from the board
    # Will need to pre-populate these in the database because I don't know
    # how to detect them.
    current_status = False
    while True:

        last_status = current_status
        current_status = get_status(room_id)

        if current_status != last_status:

            s = json.loads(current_status)
            for module in s['modules']:
                bus.write_byte(
                    module['i2c_address'],
                    from_code(module['status'], led_module_dict()) if module['type'].upper() == "LED"
                    else from_code(module['status'], blind_module_dict())
                )


# gets the status for polling because fuck me
def get_status(room_id):
    req = urllib.request.Request(url=base_url + '/rooms/' + str(room_id))
    res = urllib.request.urlopen(req)
    return res.read().decode('utf-8')


def led_module_dict():
    return {
        "ERROR": 0,
        "RGB_FADE_1": 1,
        "WHITE": 2,
        "RGB_COLOR_WIPE": 3,
        "RGB_FADE_2": 4,
        "OFF": 5
    }


def blind_module_dict():
    return {
        "DOWN": 0,
        "UP": 1,
        "IDLE": 2
    }


def from_word(word, dictionary):
    return dictionary[word]


def from_code(code, dictionary):
    return list(dictionary.keys())[code]


main()
