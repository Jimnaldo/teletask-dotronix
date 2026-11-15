"""Teletask cover platform — MOTOR components (blinds, shutters, garage doors)."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import FunctionCode
from .const import DOMAIN
from .entity import TeletaskEntity
from .hub import TeletaskHub

_LOGGER = logging.getLogger(__name__)


def _to_ha(position: int) -> int:
    """Teletask position (% closed, 0 = OP) <-> HA position (% open). Symmetric."""
    return 100 - max(0, min(100, int(position)))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    hub: TeletaskHub = hass.data[DOMAIN][entry.entry_id]
    entities = [
        TeletaskCover(hub, comp)
        for fn in (FunctionCode.MOTOR, FunctionCode.MOTORGRP)
        for comp in hub.get_components_by_function(fn)
    ]
    async_add_entities(entities)


class TeletaskCover(TeletaskEntity, CoverEntity):
    """A Teletask motor exposed as a HA cover (blind/shutter)."""

    _attr_device_class = CoverDeviceClass.BLIND
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
    )

    def __init__(self, hub: TeletaskHub, component: dict) -> None:
        super().__init__(hub, component)
        if component.get("config", {}).get("tilt"):
            # Slat position (DoIP SET_SLAT_POSITION); the central doesn't report it.
            self._attr_supported_features |= CoverEntityFeature.SET_TILT_POSITION

    @property
    def extra_state_attributes(self) -> dict:
        attrs = {
            key: self._state_dict[key]
            for key in ("sun_protection", "wind_protection", "seconds_to_finish")
            if key in self._state_dict
        }
        requested = self._state_dict.get("requested_position")
        if requested is not None:
            attrs["requested_position"] = _to_ha(requested)
        return attrs

    @property
    def is_closed(self) -> bool | None:
        pos = self.current_cover_position
        if pos is None:
            return None
        return pos == 0

    @property
    def is_opening(self) -> bool:
        return (
            self._state_dict.get("state") == "ON"
            and self._state_dict.get("last_direction") == "UP"
        )

    @property
    def is_closing(self) -> bool:
        return (
            self._state_dict.get("state") == "ON"
            and self._state_dict.get("last_direction") == "DOWN"
        )

    @property
    def current_cover_position(self) -> int | None:
        """Return position 0-100 (100 = fully open)."""
        pos = self._state_dict.get("current_position")
        return None if pos is None else _to_ha(pos)

    async def async_open_cover(self, **kwargs: Any) -> None:
        await self._hub.async_set_motor(self._number, "UP", self._function)

    async def async_close_cover(self, **kwargs: Any) -> None:
        await self._hub.async_set_motor(self._number, "DOWN", self._function)

    async def async_stop_cover(self, **kwargs: Any) -> None:
        await self._hub.async_set_motor(self._number, "STOP", self._function)

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        position = kwargs.get(ATTR_POSITION, 0)
        # Dotronix: HA 100 = open, Teletask 0 % = open (position is % closed).
        await self._hub.async_set_motor_position(self._number, _to_ha(position), self._function)

    async def async_set_cover_tilt_position(self, **kwargs: Any) -> None:
        await self._hub.async_set_motor_tilt(self._function, self._number, kwargs.get(ATTR_TILT_POSITION, 0))
