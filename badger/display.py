"""E-ink display rendering for shade status."""

import badger2040

# Layout constants
WIDTH = badger2040.WIDTH    # 296
HEIGHT = badger2040.HEIGHT  # 128
MARGIN = 4
HEADER_H = 18
ROW_H = 16
BAR_W = 60
BAR_H = 8
FOOTER_H = 14


def draw_status(badge, shades, rooms, error_msg=None):
    """Draw shade status table on the e-ink display."""
    badge.set_pen(15)  # white
    badge.clear()
    badge.set_pen(0)   # black

    # Header bar
    badge.rectangle(0, 0, WIDTH, HEADER_H)
    badge.set_pen(15)
    badge.set_font("bitmap8")
    badge.text("PowerView", MARGIN, 5, scale=1)

    shade_count = len([s for s in shades if s["roomId"]])
    badge.text("{} shades".format(shade_count), WIDTH - 70, 5, scale=1)
    badge.set_pen(0)

    # Filter to assigned shades only
    assigned = [s for s in shades if s["roomId"] is not None]

    if error_msg:
        badge.set_font("bitmap8")
        badge.text(error_msg, MARGIN, HEADER_H + 20, scale=1)
        _draw_footer(badge)
        badge.update()
        return

    # Column headers
    y = HEADER_H + 2
    badge.set_font("bitmap6")
    badge.text("Shade", MARGIN, y, scale=1)
    badge.text("Room", 90, y, scale=1)
    badge.text("Position", 148, y, scale=1)
    badge.text("Batt", WIDTH - 35, y, scale=1)

    # Shade rows
    y += ROW_H - 2
    badge.line(MARGIN, y - 3, WIDTH - MARGIN, y - 3)

    for shade in assigned:
        if y + ROW_H > HEIGHT - FOOTER_H:
            break

        name = shade["name"]
        if len(name) > 12:
            name = name[:11] + "."

        room_name = rooms.get(shade["roomId"], "")
        if len(room_name) > 7:
            room_name = room_name[:6] + "."

        badge.text(name, MARGIN, y, scale=1)
        badge.text(room_name, 90, y, scale=1)

        # Position bar
        pct = shade["position"]
        if pct is not None:
            _draw_bar(badge, 148, y + 1, BAR_W, BAR_H, pct)
            badge.text("{}%".format(pct), 148 + BAR_W + 3, y, scale=1)
        else:
            badge.text("--", 148, y, scale=1)

        # Battery
        batt = shade["battery"]
        if batt is not None:
            badge.text("{}%".format(batt), WIDTH - 35, y, scale=1)
        else:
            badge.text("--", WIDTH - 35, y, scale=1)

        y += ROW_H

    _draw_footer(badge)
    badge.update()


def _draw_bar(badge, x, y, w, h, pct):
    """Draw a position bar."""
    badge.rectangle(x, y, w, h)      # outline
    badge.set_pen(15)
    badge.rectangle(x + 1, y + 1, w - 2, h - 2)  # white fill
    badge.set_pen(0)
    filled = max(1, round((w - 2) * pct / 100))
    badge.rectangle(x + 1, y + 1, filled, h - 2)  # black fill


def _draw_footer(badge):
    """Draw button labels at bottom."""
    y = HEIGHT - FOOTER_H
    badge.line(0, y, WIDTH, y)
    y += 3
    badge.set_font("bitmap6")
    # Three button zones: A (left), B (center), C (right)
    third = WIDTH // 3
    badge.text("[A] Morning", MARGIN, y, scale=1)
    badge.text("[B] Half", third + MARGIN, y, scale=1)
    badge.text("[C] Evening", 2 * third + MARGIN, y, scale=1)


def draw_message(badge, line1, line2=""):
    """Draw a simple centered message."""
    badge.set_pen(15)
    badge.clear()
    badge.set_pen(0)
    badge.set_font("bitmap8")
    badge.text(line1, MARGIN, HEIGHT // 2 - 12, scale=1)
    if line2:
        badge.text(line2, MARGIN, HEIGHT // 2 + 4, scale=1)
    badge.update()
