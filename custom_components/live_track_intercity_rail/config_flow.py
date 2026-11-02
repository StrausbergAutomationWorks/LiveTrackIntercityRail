"""Config flow: region, railroad, and a key for a railroad whose source wants one.
Live Track Commuter Rail's shape, with the key step.

A region appears only if at least one railroad serves it, and a railroad
already set up is not offered again. A key is checked with one read before it is
kept (Lee 2026-11-02, D1: each config entry holds its own), and the reauth step
asks for a new one when the client has given up on every key it holds. For the rest
the first refresh tells Home Assistant whether the source answers
(ConfigEntryNotReady retries on its own).
"""

from __future__ import annotations

from typing import Any, Mapping

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
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_API_KEY,
    CONF_OPERATOR,
    CONF_REGION,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .operators import OPERATORS, Operator, operators_in, regions_in_use
from .sources import tfnsw


def _dropdown(options: list[SelectOptionDict]) -> SelectSelector:
    return SelectSelector(SelectSelectorConfig(
        options=options, mode=SelectSelectorMode.DROPDOWN, sort=False))


def _key_schema() -> vol.Schema:
    return vol.Schema({vol.Required(CONF_API_KEY): TextSelector(
        TextSelectorConfig(type=TextSelectorType.PASSWORD))})


class IntercityRailConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._region: str | None = None
        self._operator: Operator | None = None

    async def _check_key(self, op: Operator, key: str) -> str | None:
        """None when the key reads the feed, else the form's error."""
        return await self.hass.async_add_executor_job(
            tfnsw.check_key, op.source_options["consumer"], key)

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
            if op.needs_key:
                self._operator = op
                return await self.async_step_key()
            return self.async_create_entry(title=op.name,
                                           data={CONF_OPERATOR: op.id})
        schema = vol.Schema({vol.Required(CONF_OPERATOR): _dropdown(
            [SelectOptionDict(value=op.id, label=op.name) for op in choices])})
        return self.async_show_form(step_id="operator", data_schema=schema)

    async def async_step_key(self, user_input: dict[str, Any] | None = None
                             ) -> ConfigFlowResult:
        op = self._operator
        errors: dict[str, str] = {}
        if user_input is not None:
            key = user_input[CONF_API_KEY].strip()
            error = await self._check_key(op, key) if key else "invalid_key"
            if error is None:
                return self.async_create_entry(title=op.name,
                                               data={CONF_OPERATOR: op.id, CONF_API_KEY: key})
            errors["base"] = error
        return self.async_show_form(
            step_id="key", data_schema=_key_schema(), errors=errors,
            description_placeholders={"name": op.name, "url": op.key_url or ""})

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None
                                        ) -> ConfigFlowResult:
        entry = self._get_reauth_entry()
        op = OPERATORS[entry.data[CONF_OPERATOR]]
        errors: dict[str, str] = {}
        if user_input is not None:
            key = user_input[CONF_API_KEY].strip()
            error = await self._check_key(op, key) if key else "invalid_key"
            if error is None:
                return self.async_update_reload_and_abort(entry, data_updates={CONF_API_KEY: key})
            errors["base"] = error
        return self.async_show_form(
            step_id="reauth_confirm", data_schema=_key_schema(), errors=errors,
            description_placeholders={"name": op.name, "url": op.key_url or ""})

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
        # The railroad's own interval when the user has not set one
        # (operators/base.py scan_interval_s; Brightline 60 s).
        op = OPERATORS.get(self.config_entry.data.get(CONF_OPERATOR, ""))
        default = op.scan_interval_s if op is not None else DEFAULT_SCAN_INTERVAL
        schema = vol.Schema({
            vol.Required(CONF_SCAN_INTERVAL,
                         default=cur.get(CONF_SCAN_INTERVAL, default)):
                NumberSelector(NumberSelectorConfig(
                    min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL, step=1,
                    unit_of_measurement="s", mode=NumberSelectorMode.BOX)),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
