"""Boot guard: hold button A during reset/plug-in to skip main.py.

This runs before main.py. If A is held, it writes a flag file
that main.py checks before starting the app loop.
"""
import machine
import os

BUTTON_A_PIN = 12
SKIP_FLAG = "skip_main"

pin = machine.Pin(BUTTON_A_PIN, machine.Pin.IN, machine.Pin.PULL_DOWN)

if pin.value():
    # Button A is held — write flag to skip main.py
    with open(SKIP_FLAG, "w") as f:
        f.write("1")
    # Flash LED to confirm
    led = machine.Pin(22, machine.Pin.OUT)
    import time
    for _ in range(6):
        led.toggle()
        time.sleep(0.1)
    led.value(0)
else:
    # Normal boot — remove flag if it exists
    try:
        os.remove(SKIP_FLAG)
    except OSError:
        pass
