"""Pydantic models for PowerView hub API responses.

Built from real API responses captured from a Gen 1 hub (firmware 1.1.857).
All name fields are Base64-encoded UTF-8 and decoded automatically.
"""

from __future__ import annotations

import base64

from pydantic import BaseModel, ConfigDict, field_validator


def _decode_name(v: str) -> str:
    """Decode a Base64-encoded UTF-8 name field."""
    return base64.b64decode(v).decode("utf-8")


class ShadePosition(BaseModel):
    """Shade rail position. May be absent if shade hasn't been polled."""

    model_config = ConfigDict(extra="ignore")

    posKind1: int = 1
    position1: int = 0
    posKind2: int | None = None
    position2: int | None = None

    @property
    def primary_pct(self) -> int:
        """Primary rail position as 0-100 percentage."""
        return round(self.position1 / 65535 * 100)

    @property
    def secondary_pct(self) -> int | None:
        """Secondary rail position as 0-100 percentage, if present."""
        if self.position2 is None:
            return None
        return round(self.position2 / 65535 * 100)


class Shade(BaseModel):
    """A single shade from GET /api/shades or GET /api/shades/{id}.

    Real response fields observed:
    - id, name (base64), roomId, groupId, order, type
    - batteryStrength (0-200), batteryStatus (0-3)
    - positions (may be empty {} or absent in bulk list)
    - timedOut (present on ?refresh=true when shade doesn't respond)
    - firmware (present on some responses)
    """

    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    roomId: int | None = None
    groupId: int | None = None
    order: int | None = None
    type: int = 0
    batteryStrength: int = 0
    batteryStatus: int = 0
    positions: ShadePosition | None = None
    timedOut: bool = False

    @field_validator("name", mode="before")
    @classmethod
    def decode_name(cls, v: str) -> str:
        return _decode_name(v)

    @field_validator("positions", mode="before")
    @classmethod
    def parse_positions(cls, v: dict | None) -> dict | None:
        if isinstance(v, dict) and not v:
            return None
        return v

    @property
    def battery_pct(self) -> int:
        """Battery level as 0-100 percentage."""
        return min(self.batteryStrength, 200) // 2

    @property
    def has_position(self) -> bool:
        """Whether we have position data for this shade."""
        return self.positions is not None


class Scene(BaseModel):
    """A scene from GET /api/scenes."""

    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    roomId: int
    networkNumber: int | None = None
    order: int = 0
    colorId: int = 0
    iconId: int = 0

    @field_validator("name", mode="before")
    @classmethod
    def decode_name(cls, v: str) -> str:
        return _decode_name(v)


class SceneCollection(BaseModel):
    """A scene collection (multi-scene) from GET /api/scenecollections."""

    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    order: int = 0
    colorId: int = 0
    iconId: int = 0

    @field_validator("name", mode="before")
    @classmethod
    def decode_name(cls, v: str) -> str:
        return _decode_name(v)


class Room(BaseModel):
    """A room from GET /api/rooms."""

    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    order: int = 0
    colorId: int = 0
    iconId: int = 0

    @field_validator("name", mode="before")
    @classmethod
    def decode_name(cls, v: str) -> str:
        return _decode_name(v)


class ScheduledEvent(BaseModel):
    """A hub-side scheduled event from GET /api/scheduledevents."""

    model_config = ConfigDict(extra="ignore")

    id: int
    enabled: bool
    sceneCollectionId: int
    daySunday: bool = False
    dayMonday: bool = False
    dayTuesday: bool = False
    dayWednesday: bool = False
    dayThursday: bool = False
    dayFriday: bool = False
    daySaturday: bool = False
    eventType: int = 0
    hour: int = 0
    minute: int = 0

    @property
    def days_list(self) -> list[str]:
        """Active days as short names."""
        days = []
        for attr, label in [
            ("daySunday", "Sun"),
            ("dayMonday", "Mon"),
            ("dayTuesday", "Tue"),
            ("dayWednesday", "Wed"),
            ("dayThursday", "Thu"),
            ("dayFriday", "Fri"),
            ("daySaturday", "Sat"),
        ]:
            if getattr(self, attr):
                days.append(label)
        return days

    @property
    def time_str(self) -> str:
        return f"{self.hour:02d}:{self.minute:02d}"


class FirmwareVersion(BaseModel):
    """Firmware info from GET /api/fwversion."""

    model_config = ConfigDict(extra="ignore")

    name: str = ""
    revision: int = 0
    subRevision: int = 0
    build: int = 0

    @property
    def version_str(self) -> str:
        return f"{self.revision}.{self.subRevision}.{self.build}"


class UserData(BaseModel):
    """Hub user data from GET /api/userdata."""

    model_config = ConfigDict(extra="ignore")

    serialNumber: str = ""
    hubName: str = ""
    macAddress: str = ""
    ip: str = ""
    roomCount: int = 0
    shadeCount: int = 0
    sceneCount: int = 0
    multiSceneCount: int = 0
    scheduledEventCount: int = 0
    groupCount: int = 0
    rfID: str = ""
    enableScheduledEvents: bool = False
    setupCompleted: bool = False
    unassignedShadeCount: int = 0

    @field_validator("hubName", mode="before")
    @classmethod
    def decode_name(cls, v: str) -> str:
        if v:
            return _decode_name(v)
        return v
