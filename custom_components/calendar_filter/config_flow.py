from typing import Any, Mapping, cast

import voluptuous as vol

from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
)
from homeassistant.core import callback

from . import DOMAIN


CONFIG_FLOW = {
    "user": SchemaFlowFormStep(
        vol.Schema(
            {
                vol.Required("name"): selector.TextSelector(
                    selector.TextSelectorConfig()
                ),
                vol.Required("calendar_entity"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="calendar")
                ),  # The calendar entity to filter
                vol.Required("template"): selector.TemplateSelector(
                    selector.TemplateSelectorConfig()
                ),  # Template to filter events
            }
        ),
    ),
}


OPTIONS_FLOW = {
    "init": SchemaFlowFormStep(
        vol.Schema(
            {
                vol.Required("name"): selector.TextSelector(
                    selector.TextSelectorConfig()
                ),
                vol.Required("calendar_entity"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="calendar")
                ),  # The calendar entity to filter
                vol.Required("template"): selector.TemplateSelector(
                    selector.TemplateSelectorConfig()
                ),  # Template to filter events
            }
        ),
    ),
}


class CalendarFilterConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle config flow for template helper."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    @callback
    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""
        return cast(str, options["name"])


# class CalendarFilterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
#     VERSION = 1

#     async def async_step_user(self, user_input=None):
#         errors = {}
#         if user_input is not None:
#             return self.async_create_entry(title=user_input["name"], data=user_input)

#         return self.async_show_form(
#             step_id="user",
#             data_schema=vol.Schema(
#                 {
#                     vol.Required("name"): selector.TextSelector(
#                         selector.TextSelectorConfig()
#                     ),
#                     vol.Required("calendar_entity"): selector.EntitySelector(
#                         selector.EntitySelectorConfig(domain="calendar")
#                     ),  # The calendar entity to filter
#                     vol.Required("template"): selector.TemplateSelector(
#                         selector.TemplateSelectorConfig()
#                     ),  # Template to filter events
#                 }
#             ),
#             errors=errors,
#         )

#     async def async_step_reconfigure(self, user_input=None):
#         errors = {}
#         config_entry = self.hass.config_entries.async_get_entry(
#             self.context["entry_id"]
#         )
#         if user_input is not None:
#             return self.async_update_reload_and_abort(
#                 entry=config_entry,
#                 title=user_input["name"],
#                 data=user_input,
#             )

#         return self.async_show_form(
#             step_id="reconfigure",
#             data_schema=vol.Schema(
#                 {
#                     vol.Required("name"): selector.TextSelector(
#                         selector.TextSelectorConfig()
#                     ),
#                     vol.Required("calendar_entity"): selector.EntitySelector(
#                         selector.EntitySelectorConfig(domain="calendar")
#                     ),  # The calendar entity to filter
#                     vol.Required("template"): selector.TemplateSelector(
#                         selector.TemplateSelectorConfig()
#                     ),  # Template to filter events
#                 }
#             ),
#             errors=errors,
#         )
