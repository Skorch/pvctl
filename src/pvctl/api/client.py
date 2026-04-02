"""HTTP client wrapper for PowerView hub API.

Synchronous httpx client with timeout, retry on connection errors,
and user-friendly error messages.
"""

from __future__ import annotations

import httpx

from pvctl.api.models import (
    FirmwareVersion,
    Room,
    Scene,
    SceneCollection,
    ScheduledEvent,
    Shade,
    UserData,
)

DEFAULT_TIMEOUT = 10.0
REFRESH_TIMEOUT = 30.0
MAX_RETRIES = 1


class HubError(Exception):
    """Raised when the hub is unreachable or returns an unexpected response."""


class HubClient:
    """Synchronous client for the PowerView hub REST API."""

    def __init__(self, hub_ip: str, *, verbose: bool = False) -> None:
        self.hub_ip = hub_ip
        self.base_url = f"http://{hub_ip}/api"
        self.verbose = verbose
        self._client = httpx.Client(timeout=DEFAULT_TIMEOUT)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> HubClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
        timeout: float | None = None,
    ) -> dict:
        """Make an HTTP request with retry on connection errors."""
        url = f"{self.base_url}/{path}"
        kwargs: dict = {}
        if params:
            kwargs["params"] = params
        if json:
            kwargs["json"] = json
        if timeout:
            kwargs["timeout"] = timeout

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                if self.verbose:
                    import sys
                    print(f"  {method} {url} {kwargs}", file=sys.stderr)
                response = self._client.request(method, url, **kwargs)
                response.raise_for_status()
                # Some endpoints return empty body on success (e.g. scene collection activation)
                text = response.text.strip()
                if not text or text == "{}":
                    return {}
                return response.json()
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    continue
            except httpx.HTTPStatusError as e:
                raise HubError(f"Hub returned {e.response.status_code} for {method} {url}") from e

        raise HubError(
            f"Hub not reachable at {self.hub_ip}. Check network and hub power."
        ) from last_error

    def _get(self, path: str, **kwargs: object) -> dict:
        return self._request("GET", path, **kwargs)

    def _put(self, path: str, **kwargs: object) -> dict:
        return self._request("PUT", path, **kwargs)

    # --- Hub info ---

    def get_userdata(self) -> UserData:
        data = self._get("userdata")
        return UserData.model_validate(data["userData"])

    def get_firmware(self) -> FirmwareVersion:
        data = self._get("fwversion")
        return FirmwareVersion.model_validate(data["firmware"]["mainProcessor"])

    # --- Shades ---

    def get_shades(self) -> list[Shade]:
        data = self._get("shades")
        return [Shade.model_validate(s) for s in data.get("shadeData", [])]

    def get_shade(self, shade_id: int, *, refresh: bool = False) -> Shade:
        params = {"refresh": "true"} if refresh else None
        timeout = REFRESH_TIMEOUT if refresh else None
        data = self._get(f"shades/{shade_id}", params=params, timeout=timeout)
        return Shade.model_validate(data["shade"])

    def set_shade_position(self, shade_id: int, position1: int, pos_kind1: int = 1) -> Shade:
        body = {"shade": {"positions": {"posKind1": pos_kind1, "position1": position1}}}
        data = self._put(f"shades/{shade_id}", json=body)
        if "shade" in data:
            return Shade.model_validate(data["shade"])
        # Re-fetch if PUT doesn't return shade data
        return self.get_shade(shade_id)

    def jog_shade(self, shade_id: int) -> dict:
        return self._put(f"shades/{shade_id}", json={"shade": {"motion": "jog"}})

    def stop_shade(self, shade_id: int) -> dict:
        return self._put(f"shades/{shade_id}", json={"shade": {"motion": "stop"}})

    # --- Scenes ---

    def get_scenes(self) -> list[Scene]:
        data = self._get("scenes")
        return [Scene.model_validate(s) for s in data.get("sceneData", [])]

    def activate_scene(self, scene_id: int) -> dict:
        return self._get("scenes", params={"sceneid": scene_id})

    # --- Scene Collections ---

    def get_scene_collections(self) -> list[SceneCollection]:
        data = self._get("scenecollections")
        return [SceneCollection.model_validate(s) for s in data.get("sceneCollectionData", [])]

    def activate_scene_collection(self, collection_id: int) -> dict:
        return self._get("scenecollections", params={"sceneCollectionId": collection_id})

    # --- Rooms ---

    def get_rooms(self) -> list[Room]:
        data = self._get("rooms")
        return [Room.model_validate(r) for r in data.get("roomData", [])]

    # --- Scheduled Events ---

    def get_scheduled_events(self) -> list[ScheduledEvent]:
        data = self._get("scheduledevents")
        return [
            ScheduledEvent.model_validate(e)
            for e in data.get("scheduledEventData", [])
        ]

    def set_schedule_enabled(self, event_id: int, enabled: bool) -> ScheduledEvent:
        data = self._put(
            f"scheduledevents/{event_id}",
            json={"scheduledEvent": {"enabled": enabled}},
        )
        return ScheduledEvent.model_validate(data["scheduledEvent"])
