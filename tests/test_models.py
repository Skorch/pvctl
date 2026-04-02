"""Test Pydantic models against real API response data."""

from pvctl.api.models import (
    FirmwareVersion,
    Room,
    Scene,
    SceneCollection,
    ScheduledEvent,
    Shade,
    UserData,
)
from tests.conftest import (
    FWVERSION_RESPONSE,
    ROOMS_LIST_RESPONSE,
    SCENE_COLLECTIONS_RESPONSE,
    SCENES_LIST_RESPONSE,
    SCHEDULED_EVENTS_RESPONSE,
    SHADE_REFRESH_TIMEDOUT_RESPONSE,
    SHADE_WITH_POSITION,
    SHADES_LIST_RESPONSE,
    USERDATA_RESPONSE,
)


class TestShadeModel:
    def test_parse_shade_list(self):
        shades = [Shade.model_validate(s) for s in SHADES_LIST_RESPONSE["shadeData"]]
        assert len(shades) == 3
        assert shades[0].name == "Anna Small"
        assert shades[0].id == 50594
        assert shades[0].type == 5
        assert shades[0].roomId == 46688

    def test_shade_without_room(self):
        """Shade 8 (type 252) has no roomId — phantom/unassigned."""
        shades = [Shade.model_validate(s) for s in SHADES_LIST_RESPONSE["shadeData"]]
        phantom = shades[2]
        assert phantom.name == "Shade 8"
        assert phantom.roomId is None
        assert phantom.type == 252

    def test_shade_empty_positions_becomes_none(self):
        """Bulk list returns positions: {} — should parse as None."""
        shade_data = {**SHADES_LIST_RESPONSE["shadeData"][0], "positions": {}}
        shade = Shade.model_validate(shade_data)
        assert shade.positions is None
        assert shade.has_position is False

    def test_shade_with_position(self):
        shade = Shade.model_validate(SHADE_WITH_POSITION)
        assert shade.has_position is True
        assert shade.positions.position1 == 65535
        assert shade.positions.primary_pct == 100

    def test_shade_timedout(self):
        shade = Shade.model_validate(SHADE_REFRESH_TIMEDOUT_RESPONSE["shade"])
        assert shade.timedOut is True

    def test_battery_pct(self):
        shade = Shade.model_validate(SHADES_LIST_RESPONSE["shadeData"][1])
        assert shade.batteryStrength == 179
        assert shade.battery_pct == 89

    def test_battery_pct_zero(self):
        shade = Shade.model_validate(SHADES_LIST_RESPONSE["shadeData"][0])
        assert shade.batteryStrength == 0
        assert shade.battery_pct == 0

    def test_extra_fields_ignored(self):
        data = {**SHADES_LIST_RESPONSE["shadeData"][0], "unknownField": "whatever"}
        shade = Shade.model_validate(data)
        assert shade.name == "Anna Small"


class TestSceneModel:
    def test_parse_scene_list(self):
        scenes = [Scene.model_validate(s) for s in SCENES_LIST_RESPONSE["sceneData"]]
        assert len(scenes) == 2
        assert scenes[0].name == "Master Up"
        assert scenes[0].id == 38772
        assert scenes[1].name == "Movie"


class TestSceneCollectionModel:
    def test_parse_collection_list(self):
        collections = [
            SceneCollection.model_validate(s)
            for s in SCENE_COLLECTIONS_RESPONSE["sceneCollectionData"]
        ]
        assert len(collections) == 2
        assert collections[0].name == "Morning Up Master Lila"
        assert collections[1].name == "Evening Down"


class TestRoomModel:
    def test_parse_room_list(self):
        rooms = [Room.model_validate(r) for r in ROOMS_LIST_RESPONSE["roomData"]]
        assert len(rooms) == 4
        names = [r.name for r in rooms]
        assert names == ["Twins", "Lila", "Master", "Media"]


class TestScheduledEventModel:
    def test_parse_events(self):
        events = [
            ScheduledEvent.model_validate(e)
            for e in SCHEDULED_EVENTS_RESPONSE["scheduledEventData"]
        ]
        assert len(events) == 2
        assert events[0].enabled is True
        assert events[0].time_str == "10:00"
        assert events[0].days_list == ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    def test_scene_collection_id(self):
        event = ScheduledEvent.model_validate(
            SCHEDULED_EVENTS_RESPONSE["scheduledEventData"][0]
        )
        assert event.sceneCollectionId == 24565


class TestUserDataModel:
    def test_parse_userdata(self):
        ud = UserData.model_validate(USERDATA_RESPONSE["userData"])
        assert ud.hubName == "Paisley3044"
        assert ud.serialNumber == "51EEA91134B1A057"
        assert ud.ip == "192.168.7.38"
        assert ud.shadeCount == 8
        assert ud.roomCount == 4
        assert ud.sceneCount == 11


class TestFirmwareModel:
    def test_parse_firmware(self):
        fw = FirmwareVersion.model_validate(
            FWVERSION_RESPONSE["firmware"]["mainProcessor"]
        )
        assert fw.version_str == "1.1.857"
        assert fw.name == "PowerView Hub"
