#!/usr/bin/python3
import json
from subprocess import run

server = "voyage.lan"

topic = "radiator_controller"

msg = {"cmd": "turn_on", "args": None}

msg = json.dumps(msg)
cmd = ["mosquitto_pub", "-h", server, "-t", topic, "-m", msg]
print(" ".join(cmd))
run(cmd)
