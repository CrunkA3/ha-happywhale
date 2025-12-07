import logging
import aiohttp
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass
)

from homeassistant.core import (
    HomeAssistant,
    callback
)

from .coordinator import (
    WhaleTrackingCoordinator,
)

from .const import (
    DOMAIN,
    CONF_WHALE_ID,
    MANUFACTURER,
    MODEL,
    NAME
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the whale tracker from a config entry."""
    whale_id = entry.data[CONF_WHALE_ID]

    whale_tracking_coordinator = WhaleTrackingCoordinator(hass, entry, whale_id)
    await whale_tracking_coordinator.async_config_entry_first_refresh()

    async_add_entities([
        GPSSensor(whale_tracking_coordinator, whale_id),
        ])





class GPSSensor(TrackerEntity, CoordinatorEntity):
    def __init__(self, coordinator, whale_id):
        super().__init__(coordinator, context=0)

        self._location_accuracy = None
        self._battery_level = None
        self._source_type = SourceType.GPS
        self._device_id = f"happywhale_tracker_{whale_id}"


    async def async_update(self):
        """Synchronize state"""
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    @property
    def name(self):
        result = self.coordinator._whale_id

        if not self.individual is None and self.individual != "none":
            if not self.individual["nickname"] is None and self.individual["nickname"] != "none":
                result = self.individual["nickname"]
            else:
                result = self.individual["species"]
                
        return result

    @property
    def unique_id(self):
        return self._device_id

    @property
    def icon(self):
        return "mdi:alert" if self.state is None or self.state == "none" else "mdi:fish"


    @property
    def device_info(self):
        """Get information about this device."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": NAME,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    @property
    def lastEncounter(self):
        if self.coordinator.data is None or self.coordinator.data == "none":
            return None

        if self.coordinator.data["stats"] is None or self.coordinator.data["stats"] == "none":
            return None

        return self.coordinator.data["stats"]["lastEnc"]

    @property
    def individual(self):
        if self.coordinator.data is None or self.coordinator.data == "none":
            return None

        return self.coordinator.data["individual"]

    @property
    def encounters(self):
        """All encounters of the whale."""
        if self.coordinator.data is None or self.coordinator.data == "none":
            return None

        return self.coordinator.data["encounters"]


    @property
    def latitude(self):
        return None if self.lastEncounter is None or self.lastEncounter == "none" else self.lastEncounter["latlng"][0]

    @property
    def longitude(self):
        return None if self.lastEncounter is None or self.lastEncounter == "none" else self.lastEncounter["latlng"][1]

    @property
    def location_name(self):
        return None if self.lastEncounter is None or self.lastEncounter == "none" else self.lastEncounter["region"]

    @property
    def location_accuracy(self):
        return self._location_accuracy

    @property
    def battery_level(self):
        return self._battery_level

    @property
    def source_type(self):
        return self._source_type

    @property
    def species(self) -> str | None:
        """Specis name of the whale."""
        return None if self.individual is None or self.individual == "none" else self.individual["species"]



    @property
    def state(self):
        """Return the state of the sensor."""
        return f"Lat: {self.latitude}, Lon: {self.longitude}"


    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        
        encounters = None

        if not self.encounters is None:
            encounters = [encounter["latlng"] for encounter in self.encounters if "latlng" in encounter]
            _LOGGER.warn(encounters)

        attrs = {
            "Encounters": encounters
        }

        return attrs
