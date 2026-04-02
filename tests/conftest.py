"""Shared test fixtures with real API response data."""


# Real responses captured from hub at 192.168.7.38 (firmware 1.1.857)

USERDATA_RESPONSE = {
    "userData": {
        "serialNumber": "51EEA91134B1A057",
        "rfID": "0x5F89",
        "rfIDInt": 24457,
        "rfStatus": 0,
        "hubName": "UGFpc2xleTMwNDQ=",  # "Paisley3044"
        "macAddress": "00:26:74:18:e0:8d",
        "roomCount": 4,
        "shadeCount": 8,
        "groupCount": 6,
        "sceneCount": 11,
        "sceneMemberCount": 20,
        "multiSceneCount": 4,
        "multiSceneMemberCount": 10,
        "scheduledEventCount": 4,
        "sceneControllerCount": 0,
        "sceneControllerMemberCount": 0,
        "accessPointCount": 0,
        "localTimeDataSet": True,
        "enableScheduledEvents": True,
        "remoteConnectEnabled": True,
        "editingEnabled": True,
        "setupCompleted": False,
        "gateway": "192.168.7.1",
        "mask": "255.255.255.0",
        "ip": "192.168.7.38",
        "dns": "8.8.8.8",
        "staticIp": False,
        "addressKind": "newPrimary",
        "unassignedShadeCount": 1,
        "undefinedShadeCount": 1,
    }
}

FWVERSION_RESPONSE = {
    "firmware": {
        "mainProcessor": {
            "name": "PowerView Hub",
            "revision": 1,
            "subRevision": 1,
            "build": 857,
        }
    }
}

SHADES_LIST_RESPONSE = {
    "shadeIds": [50594, 16611, 30279, 52702, 44165, 51265, 9049, 16396],
    "shadeData": [
        {
            "id": 50594,
            "name": "QW5uYSBTbWFsbA==",  # "Anna Small"
            "roomId": 46688,
            "groupId": 12777,
            "order": 0,
            "type": 5,
            "batteryStrength": 0,
            "batteryStatus": 0,
        },
        {
            "id": 30279,
            "name": "TWFzdGVyIDE=",  # "Master 1"
            "roomId": 5624,
            "groupId": 11983,
            "order": 2,
            "type": 5,
            "batteryStrength": 179,
            "batteryStatus": 3,
        },
        {
            "id": 16396,
            "name": "U2hhZGUgOA==",  # "Shade 8" — phantom, no roomId
            "order": 7,
            "type": 252,
            "batteryStrength": 0,
            "batteryStatus": 0,
        },
    ],
}

SHADE_SINGLE_RESPONSE = {
    "shade": {
        "id": 50594,
        "name": "QW5uYSBTbWFsbA==",
        "roomId": 46688,
        "groupId": 12777,
        "order": 0,
        "type": 5,
        "batteryStrength": 0,
        "batteryStatus": 0,
    },
}

SHADE_REFRESH_TIMEDOUT_RESPONSE = {
    "shade": {
        "id": 50594,
        "name": "QW5uYSBTbWFsbA==",
        "roomId": 46688,
        "groupId": 12777,
        "order": 0,
        "type": 5,
        "timedOut": True,
        "batteryStrength": 0,
        "batteryStatus": 0,
    }
}

SHADE_WITH_POSITION = {
    "id": 30279,
    "name": "TWFzdGVyIDE=",
    "roomId": 5624,
    "groupId": 11983,
    "order": 2,
    "type": 5,
    "batteryStrength": 179,
    "batteryStatus": 3,
    "positions": {
        "posKind1": 1,
        "position1": 65535,
    },
}

SCENES_LIST_RESPONSE = {
    "sceneIds": [38772, 15890, 18241, 28507, 21454],
    "sceneData": [
        {
            "id": 38772,
            "networkNumber": 1,
            "name": "TWFzdGVyIFVw",  # "Master Up"
            "roomId": 5624,
            "order": 0,
            "colorId": 4,
            "iconId": 0,
        },
        {
            "id": 21454,
            "networkNumber": 9,
            "name": "TW92aWU=",  # "Movie"
            "roomId": 21454,
            "order": 8,
            "colorId": 15,
            "iconId": 0,
        },
    ],
}

SCENE_ACTIVATE_RESPONSE = {"scene": {"shadeIds": [52702]}}

SCENE_COLLECTIONS_RESPONSE = {
    "sceneCollectionIds": [24565, 15890, 49901, 1683],
    "sceneCollectionData": [
        {
            "id": 24565,
            "name": "TW9ybmluZyBVcCBNYXN0ZXIgTGlsYQ==",  # "Morning Up Master Lila"
            "order": 0,
            "colorId": 3,
            "iconId": 96,
        },
        {
            "id": 15890,
            "name": "RXZlbmluZyBEb3du",  # "Evening Down"
            "order": 1,
            "colorId": 0,
            "iconId": 97,
        },
    ],
}

ROOMS_LIST_RESPONSE = {
    "roomIds": [46688, 17480, 5624, 21454],
    "roomData": [
        {"id": 46688, "name": "VHdpbnM=", "order": 0, "colorId": 0, "iconId": 0},
        {"id": 17480, "name": "TGlsYQ==", "order": 1, "colorId": 1, "iconId": 0},
        {"id": 5624, "name": "TWFzdGVy", "order": 2, "colorId": 6, "iconId": 0},
        {"id": 21454, "name": "TWVkaWE=", "order": 3, "colorId": 15, "iconId": 34},
    ],
}

SCHEDULED_EVENTS_RESPONSE = {
    "scheduledEventIds": [20625, 23805, 42747, 17520],
    "scheduledEventData": [
        {
            "id": 20625,
            "enabled": True,
            "sceneCollectionId": 24565,
            "daySunday": True,
            "dayMonday": True,
            "dayTuesday": True,
            "dayWednesday": True,
            "dayThursday": True,
            "dayFriday": True,
            "daySaturday": True,
            "eventType": 0,
            "hour": 10,
            "minute": 0,
        },
        {
            "id": 17520,
            "enabled": True,
            "sceneCollectionId": 15890,
            "daySunday": True,
            "dayMonday": True,
            "dayTuesday": True,
            "dayWednesday": True,
            "dayThursday": True,
            "dayFriday": True,
            "daySaturday": True,
            "eventType": 0,
            "hour": 20,
            "minute": 0,
        },
    ],
}
