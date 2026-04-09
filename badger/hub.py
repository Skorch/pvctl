"""PowerView hub API client for MicroPython."""

import urequests
import socket
from ubinascii import a2b_base64


def decode_name(b64):
    """Decode Base64-encoded UTF-8 name."""
    try:
        return a2b_base64(b64).decode("utf-8")
    except:
        return "?"


def get_shades(hub_ip):
    """Fetch all shades. Returns list of dicts with decoded names."""
    r = urequests.get("http://{}/api/shades".format(hub_ip))
    data = r.json()
    r.close()
    shades = []
    for s in data.get("shadeData", []):
        pos = s.get("positions", {})
        p1 = pos.get("position1")
        pct = round(p1 / 65535 * 100) if p1 is not None else None
        batt_raw = s.get("batteryStrength", 0)
        batt = min(batt_raw, 200) // 2 if batt_raw > 0 else None
        shades.append({
            "id": s["id"],
            "name": decode_name(s.get("name", "")),
            "roomId": s.get("roomId"),
            "position": pct,
            "battery": batt,
            "type": s.get("type", 0),
        })
    return shades


def get_rooms(hub_ip):
    """Fetch rooms. Returns dict of id -> name."""
    r = urequests.get("http://{}/api/rooms".format(hub_ip))
    data = r.json()
    r.close()
    return {
        rm["id"]: decode_name(rm.get("name", ""))
        for rm in data.get("roomData", [])
    }


def activate_collection(hub_ip, collection_id):
    """Activate a scene collection using raw socket.

    The hub returns quirky HTTP responses that urequests can't parse,
    so we use a raw socket and just check if we got any response.
    """
    path = "/api/scenecollections?sceneCollectionId={}".format(collection_id)
    addr = socket.getaddrinfo(hub_ip, 80)[0][-1]
    s = socket.socket()
    s.settimeout(10)
    try:
        s.connect(addr)
        request = "GET {} HTTP/1.0\r\nHost: {}\r\n\r\n".format(path, hub_ip)
        s.send(request.encode())
        response = s.recv(1024).decode()
        s.close()
        return "200" in response
    except Exception:
        try:
            s.close()
        except:
            pass
        raise
