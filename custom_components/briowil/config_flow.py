"""Configuration UI: accepts the BrioWil controller IP and refresh interval."""

import voluptuous as vol

from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONF_SERVER_IP,
    CONF_REFRESH_INTERVAL,
    DEFAULT_REFRESH_INTERVAL,
    MIN_REFRESH_INTERVAL,
    MAX_REFRESH_INTERVAL,
)


class BrioWilConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry,
    ):
        return BrioWilOptionsFlow()

    async def async_step_user(
        self,
        user_input=None,
    ):

        if user_input is not None:

            return self.async_create_entry(
                title="BrioWil Server",
                data={
                    CONF_SERVER_IP:
                        user_input[
                            CONF_SERVER_IP
                        ]
                },
                options={
                    CONF_REFRESH_INTERVAL:
                        DEFAULT_REFRESH_INTERVAL
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SERVER_IP
                    ): str
                }
            ),
        )


class BrioWilOptionsFlow(
    config_entries.OptionsFlow,
):

    async def async_step_init(
        self,
        user_input=None,
    ):

        if user_input is not None:

            return self.async_create_entry(
                title="",
                data=user_input,
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_REFRESH_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_REFRESH_INTERVAL,
                            DEFAULT_REFRESH_INTERVAL,
                        ),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(
                            min=MIN_REFRESH_INTERVAL,
                            max=MAX_REFRESH_INTERVAL,
                        ),
                    )
                }
            ),
        )