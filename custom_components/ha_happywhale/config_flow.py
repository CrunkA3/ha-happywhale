import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_WHALE_ID

class HappyWhaleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for happywhale tracker."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_WHALE_ID], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_WHALE_ID, default="28878"): cv.string,
            }),
        )
