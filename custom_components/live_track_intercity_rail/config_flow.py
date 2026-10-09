"""Config flow: region, then railroad. Live Track Commuter Rail's shape.

A region appears only if at least one railroad serves it, and a railroad
already set up is not offered again. No source here needs a key, so there is
no credentials step; the first refresh tells Home Assistant whether the
source answers (ConfigEntryNotReady retries on its own).
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_OPERATOR,
    CONF_REGION,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .operators import OPERATORS, Operator, operators_in, regions_in_use


def _dropdown(options: list[SelectOptionDict]) -> SelectSelector:
    return SelectSelector(SelectSelectorConfig(
        options=options, mode=SelectSelectorMode.DROPDOWN, sort=False))


class IntercityRailConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._region: str | None = None

    def _available(self, region: str) -> list[Operator]:
        taken = self._async_current_ids()
        return [op for op in operators_in(region) if op.id not in taken]

    async def async_step_user(self, user_input: dict[str, Any] | None = None
                              ) -> ConfigFlowResult:
        regions = {code: label for code, label in regions_in_use().items()
                   if self._available(code)}
        if not regions:
            return self.async_abort(reason="all_configured")
        if user_input is not None:
            self._region = user_input[CONF_REGION]
            return await self.async_step_operator()
        schema = vol.Schema({vol.Required(CONF_REGION): _dropdown(
            [SelectOptionDict(value=c, label=l) for c, l in regions.items()])})
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_operator(self, user_input: dict[str, Any] | None = None
                                  ) -> ConfigFlowResult:
        choices = self._available(self._region or "")
        if user_input is not None:
            op = OPERATORS[user_input[CONF_OPERATOR]]
            await self.async_set_unique_id(op.id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=op.name,
                                           data={CONF_OPERATOR: op.id})
        schema = vol.Schema({vol.Required(CONF_OPERATOR): _dropdown(
            [SelectOptionDict(value=op.id, label=op.name) for op in choices])})
        return self.async_show_form(step_id="operator", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return IntercityRailOptionsFlow()


class IntercityRailOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None
                              ) -> ConfigFlowResult:
        if user_input is not None:
            user_input[CONF_SCAN_INTERVAL] = int(user_input[CONF_SCAN_INTERVAL])
            return self.async_create_entry(title="", data=user_input)
        cur = self.config_entry.options
        schema = vol.Schema({
            vol.Required(CONF_SCAN_INTERVAL,
                         default=cur.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)):
                NumberSelector(NumberSelectorConfig(
                    min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL, step=1,
                    unit_of_measurement="s", mode=NumberSelectorMode.BOX)),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
