"""pvctl Badger 2040 W — shade status display + scene buttons.

Hold button A during reset/plug-in to skip this and drop to REPL.
"""

import time
import machine
import os

# --- Dev mode check: boot.py sets this flag if A was held ---
try:
    os.stat("skip_main")
    # Flag exists — don't run, drop to REPL for development
    print("Dev mode: skipping main.py (hold A detected)")
    print("Delete 'skip_main' file or reboot without A to resume normal operation")
except OSError:
    pass  # No flag, continue normally
else:
    import sys
    sys.exit()

import badger2040
from config import HUB_IP, POLL_INTERVAL, BUTTON_SCENES
from display import draw_status, draw_message
from hub import get_shades, get_rooms, activate_collection


def connect_wifi(badge):
    """Connect to WiFi using Badger's built-in WIFI_CONFIG.py."""
    draw_message(badge, "Connecting WiFi...")
    try:
        badge.connect()
        ip = badge.ip_address()
        draw_message(badge, "WiFi connected", ip)
        time.sleep(1)
        return True
    except Exception as e:
        draw_message(badge, "WiFi failed!", str(e)[:30])
        return False


def poll_and_display(badge):
    """Fetch shade data from hub and update display."""
    try:
        shades = get_shades(HUB_IP)
        rooms = get_rooms(HUB_IP)
        draw_status(badge, shades, rooms)
        return True
    except Exception as e:
        draw_status(badge, [], {}, error_msg="Hub error: {}".format(str(e)[:30]))
        return False


def handle_button(badge, button_key):
    """Activate a scene collection for a button press."""
    scene = BUTTON_SCENES.get(button_key)
    if not scene:
        return

    draw_message(badge, "Activating...", scene["name"])
    try:
        ok = activate_collection(HUB_IP, scene["id"])
        if ok:
            draw_message(badge, "Done!", scene["name"])
        else:
            draw_message(badge, "Failed!", scene["name"])
    except Exception as e:
        draw_message(badge, "Error!", str(e)[:30])
    time.sleep(2)
    poll_and_display(badge)


def main():
    badge = badger2040.Badger2040()
    badge.set_update_speed(badger2040.UPDATE_MEDIUM)

    if not connect_wifi(badge):
        time.sleep(5)
        machine.reset()

    # Initial display
    poll_and_display(badge)

    last_poll = time.time()

    while True:
        # Check buttons
        if badge.pressed(badger2040.BUTTON_A):
            handle_button(badge, "A")
            last_poll = time.time()
        elif badge.pressed(badger2040.BUTTON_B):
            handle_button(badge, "B")
            last_poll = time.time()
        elif badge.pressed(badger2040.BUTTON_C):
            handle_button(badge, "C")
            last_poll = time.time()
        elif badge.pressed(badger2040.BUTTON_UP):
            # Manual refresh
            draw_message(badge, "Refreshing...")
            poll_and_display(badge)
            last_poll = time.time()
        elif badge.pressed(badger2040.BUTTON_DOWN):
            # Show IP / status info
            import network
            wlan = network.WLAN(network.STA_IF)
            ip = wlan.ifconfig()[0] if wlan.isconnected() else "disconnected"
            draw_message(badge, "Hub: {}".format(HUB_IP), "IP: {}".format(ip))
            time.sleep(3)
            poll_and_display(badge)

        # Periodic refresh
        now = time.time()
        if now - last_poll >= POLL_INTERVAL:
            poll_and_display(badge)
            last_poll = now

        time.sleep(0.1)


main()
