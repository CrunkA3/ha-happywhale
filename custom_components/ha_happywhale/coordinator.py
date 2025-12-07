"""Coordinators for happywhale tracker."""
from __future__ import annotations

from datetime import timedelta
import logging

import aiohttp
from homeassistant.helpers.entity import Entity


from homeassistant.components.light import LightEntity
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, NAME, MANUFACTURER, MODEL

_LOGGER = logging.getLogger(__name__)

class WhaleTrackingCoordinator(DataUpdateCoordinator):
    """Whale Tracking coordinator.

    The CoordinatorEntity class provides:
        should_poll
        async_update
        async_added_to_hass
        available
    """

    def __init__(self, hass, entry, whale_id):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name=DOMAIN,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=3600),
        )

        self._hass = hass
        self._entry = entry
        self._whale_id = whale_id

        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN].setdefault(entry.entry_id, {
                    "name": entry.title,
                    "id": whale_id,
                    "model": MODEL,
                    "status": "OFFLINE"
                })

        self.data = None

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {
            "identifiers": {
                (DOMAIN, self._entry.entry_id)
                },
            "name": NAME,
            "manufacturer": MANUFACTURER,
            "model": MODEL
        }

    async def _async_setup(self) -> None:
        """Do initialization logic."""
        self.data = await self.fetch_data(self._whale_id)
        self.prereq_data = self.data

    async def _async_update_data(self):
        """Do the usual update"""
        self.data = await self.fetch_data(self._whale_id)
        return self.data

    async def fetch_data(self, whale_id):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        _LOGGER.debug("MowingInfoCoordinator _async_update_data")

        url = f"https://happywhale.com/app/cs/main/individual/get/{whale_id}"
        headers = {"accept": "application/json"}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    data = await response.json()
                    return data

            except aiohttp.ClientError as e:
                _LOGGER.warn(f"Failed to update whale tracking details: {e}")
