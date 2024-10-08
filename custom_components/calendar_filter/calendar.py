"""Support for filtering events from a calendar entity."""

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

import pytz
from homeassistant.components.calendar import (
    DOMAIN as CALENDAR_DOMAIN,
)
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, EventStateChangedData, HomeAssistant
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.template import Template

if TYPE_CHECKING:
    from homeassistant.helpers.entity_component import EntityComponent

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: dict,
    async_add_entities: AddEntitiesCallback,
    _: Any = None,
) -> bool | None:
    """Set up the calendar filter platform."""
    name = config.get("name")
    template = config.get("template")
    calendar_entity_id = config.get("calendar_entity")

    if not name or not template or not calendar_entity_id:
        _LOGGER.error("Missing required configuration items")
        return None

    calendar_filter = CalendarFilterEntity(hass, name, template, calendar_entity_id)
    async_add_entities([calendar_filter])

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool | None:
    """Set up the calendar filter platform."""
    name = config_entry.options.get("name")
    template = config_entry.options.get("template")
    calendar_entity_id = config_entry.options.get("calendar_entity")

    if not name or not template or not calendar_entity_id:
        _LOGGER.error("Missing required configuration items")
        return None

    calendar_filter = CalendarFilterEntity(
        hass,
        name,
        template,
        calendar_entity_id,
        config_entry.entry_id,
    )
    async_add_entities([calendar_filter])

    return True


class CalendarFilterEntity(CalendarEntity):
    """Representation of a filtered calendar entity."""

    _attr_supported_features = 0

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        template_string: str,
        calendar_entity_id: str,
        config_entry_id: str | None = None,
    ) -> None:
        """Initialize the calendar filter entity."""
        self.hass = hass
        self._name = name
        self._template = Template(template_string, hass)
        self._calendar_entity_id = calendar_entity_id
        self._event: CalendarEvent | None = None
        self._events: list[CalendarEvent] = []
        self._attr_unique_id = config_entry_id

        # Watch for changes to the underlying calendar entity
        async_track_state_change_event(
            hass, calendar_entity_id, self._calendar_state_changed
        )

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        return self._event

    async def _calendar_state_changed(self, _: Event[EventStateChangedData]) -> None:
        """Handle changes in the underlying calendar entity."""
        await self._update_calendar_state()

    async def async_get_events(
        self, _hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return calendar events within a date range."""
        events = await self._fetch_calendar_events(start_date, end_date)
        return self._filter_events(events)

    async def _fetch_calendar_events(
        self, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Fetch the events from the underlying calendar entity."""
        component: EntityComponent[CalendarEntity] = self.hass.data[CALENDAR_DOMAIN]
        entity = component.get_entity(self._calendar_entity_id)
        if not entity:
            _LOGGER.warning("Calendar entity %s not found.", self._calendar_entity_id)
            return []
        if not isinstance(entity, CalendarEntity):
            _LOGGER.warning(
                "Entity %s is not a calendar entity.", self._calendar_entity_id
            )
            return []
        return await entity.async_get_events(self.hass, start_date, end_date)

    def _filter_events(self, events: list[CalendarEvent]) -> list[CalendarEvent]:
        """Filter events based on the user-defined template."""
        filtered_events = []
        for event in events:
            try:
                template_result = self._template.async_render(
                    {"event": event.as_dict()}, parse_result=False
                )
                if (
                    isinstance(template_result, str)
                    and template_result.lower() == "true"
                ):
                    filtered_events.append(event)
            except TemplateError:
                _LOGGER.exception(
                    "Error rendering template for event %s in filter", event
                )
        return filtered_events

    async def _update_calendar_state(self) -> None:
        """Update the calendar state when events change."""
        tz = pytz.timezone(self.hass.config.time_zone)
        now = datetime.now(tz=tz)
        events = await self._fetch_calendar_events(now, now + timedelta(days=1))
        filtered_events = self._filter_events(events)

        if filtered_events:
            self._event = filtered_events[
                0
            ]  # Assume the next event is the first valid one
        else:
            self._event = None

        self.async_write_ha_state()
