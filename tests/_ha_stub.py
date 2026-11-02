"""Just enough of Home Assistant, voluptuous and aiohttp to run this integration's flow, store
and coordinator logic without them: what is tested is OUR branches, never HA's API. The API
names were read in the container's 2026.10.4 (bin\\ltir_nsw1_pick.txt)."""

import sys
import types


def _mod(name, **attrs):
    m = sys.modules.get(name)
    if m is None:
        m = types.ModuleType(name)
        sys.modules[name] = m
        if "." in name:
            parent, child = name.rsplit(".", 1)
            setattr(_mod(parent), child, m)
    for k, v in attrs.items():
        setattr(m, k, v)
    return m


class ConfigEntryAuthFailed(Exception):
    pass


class UpdateFailed(Exception):
    pass


class Abort(Exception):
    pass


class ConfigFlow:
    def __init_subclass__(cls, domain=None, **kw):
        super().__init_subclass__(**kw)

    hass = None
    _ids = ()
    _reauth = None
    uid = None

    def _async_current_ids(self):
        return set(self._ids)

    async def async_set_unique_id(self, uid):
        self.uid = uid

    def _abort_if_unique_id_configured(self):
        if self.uid in self._ids:
            raise Abort("already_configured")

    def async_abort(self, reason):
        return {"type": "abort", "reason": reason}

    def async_show_form(self, step_id, data_schema=None, errors=None, description_placeholders=None):
        return {"type": "form", "step_id": step_id, "errors": errors or {}, "schema": data_schema,
                "placeholders": description_placeholders}

    def async_create_entry(self, title, data):
        return {"type": "create_entry", "title": title, "data": data}

    def _get_reauth_entry(self):
        return self._reauth

    def async_update_reload_and_abort(self, entry, data_updates=None):
        entry.data = {**entry.data, **(data_updates or {})}
        return {"type": "abort", "reason": "reauth_successful"}


class _Any:
    def __init__(self, *a, **k):
        self.args, self.kw = a, k


class Selector(_Any):
    pass


class DataUpdateCoordinator:
    def __class_getitem__(cls, item):
        return cls

    def __init__(self, hass, logger, config_entry=None, name=None, update_interval=None):
        self.hass, self.config_entry = hass, config_entry


def install():
    """Stubs for whatever is not installed. Idempotent."""
    try:
        import voluptuous  # noqa: F401
    except ImportError:
        vol = _mod("voluptuous")
        vol.Schema = _Any
        vol.Required = lambda key, default=None: key
    try:
        import aiohttp  # noqa: F401
    except ImportError:
        aio = _mod("aiohttp")
        aio.ClientSession = object
        aio.ClientError = type("ClientError", (Exception,), {})
        aio.ClientTimeout = _Any
    if "homeassistant" in sys.modules and not hasattr(sys.modules["homeassistant"], "_saw_stub"):
        return
    _mod("homeassistant", _saw_stub=True)
    _mod("homeassistant.config_entries", ConfigEntry=object, ConfigFlow=ConfigFlow, ConfigFlowResult=dict, OptionsFlow=object)
    _mod("homeassistant.core", HomeAssistant=object, callback=lambda f: f)
    _mod("homeassistant.exceptions", ConfigEntryAuthFailed=ConfigEntryAuthFailed)
    _mod("homeassistant.helpers")
    _mod("homeassistant.helpers.selector", NumberSelector=Selector, NumberSelectorConfig=Selector, NumberSelectorMode=_Any,
         SelectOptionDict=dict, SelectSelector=Selector, SelectSelectorConfig=Selector, SelectSelectorMode=_Any,
         TextSelector=Selector, TextSelectorConfig=Selector,
         TextSelectorType=types.SimpleNamespace(PASSWORD="password"))
    sys.modules["homeassistant.helpers.selector"].NumberSelectorMode = types.SimpleNamespace(BOX="box")
    sys.modules["homeassistant.helpers.selector"].SelectSelectorMode = types.SimpleNamespace(DROPDOWN="dropdown")
    _mod("homeassistant.helpers.aiohttp_client", async_get_clientsession=lambda hass: None)
    _mod("homeassistant.helpers.update_coordinator", DataUpdateCoordinator=DataUpdateCoordinator, UpdateFailed=UpdateFailed)
    _mod("homeassistant.components")
    _mod("homeassistant.components.diagnostics",
         async_redact_data=lambda data, keys: {k: ("**REDACTED**" if k in keys else v) for k, v in data.items()})


class Hass:
    """What the code under test asks of hass."""

    def __init__(self, storage):
        self.data = {}
        self.config = types.SimpleNamespace(path=lambda *a: "/".join((storage,) + a[1:]) if a[0] == ".storage" else storage + "/" + a[0])

    async def async_add_executor_job(self, fn, *args):
        return fn(*args)
