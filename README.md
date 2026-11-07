# BrioWil for Home Assistant

Unofficial Home Assistant custom integration for BrioWil swimming pool LED lighting (TCP port **30302**).

## Features

- Power on/off, 11 solid-color presets, 7 lighting effects
- Home Assistant color wheel and 4 brightness levels
- Preserves the previous program when changing brightness (the hardware otherwise resets to White)
- Effect speed: Slow / Medium / Fast
- Configurable refresh frequency: 1–300 seconds (default 10)
- Eight optional diagnostic sensors (disabled for new entity registry entries)
- Redacted downloadable diagnostics and debug logging

## Install with HACS

1. Add **https://github.com/papou-github/briowil** as a HACS **Custom repository** of category **Integration**.
2. Install BrioWil, restart Home Assistant.
3. Go to **Settings → Devices & Services → Add integration**, select **BrioWil**, and enter the controller IP.
4. Ensure TCP port 30302 is reachable from Home Assistant.

## Protocol reference

| Operation | TCP payload |
| --- | --- |
| Turn on | `{"sprj":1}` |
| Turn off | `{"sprj":0}` |
| Color/program | `{"prcn":N}` |
| Brightness (0–3) | `{"plum":N}` |
| Effect speed (0–2) | `{"pspd":N}` |

Status reply uses zero-based character offsets: power=33, color hex=64:66, speed=70, brightness=71.

## Debugging

Add to `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.briowil: debug
```

Check **Settings → System → Logs**. The raw controller TCP response appears in DEBUG logs and may reveal device information; review before sharing logs publicly. The downloadable integration diagnostics redact the controller IP and raw response.

Previously registered diagnostic entities retain their registry enabled/disabled state.

## Development and validation

GitHub Actions runs Python compilation, JSON checks, basic protocol regression tests, HACS validation and hassfest. Hardware testing must be performed separately with a real BrioWil controller.

## License

MIT. Community integration, not affiliated with the device manufacturer.

## Winter mode (hivernage)

The integration uses `input_boolean.mode_hivernage`. If it does not exist,
BrioWil creates a native Home Assistant input_boolean entity at startup,
initially off, with a snowflake icon. The automatically created entity is
recreated after each restart and restores its previous state. It is not a
UI-managed Helper stored in Home Assistant's shared helper storage. An existing
helper with this entity ID is always reused untouched.

When the helper is **on**, BrioWil makes no TCP status requests and its light,
effect speed, refresh-frequency number and diagnostics are `unavailable`.
Switching it **off** requests fresh status immediately. Hardware control
commands are blocked while winter mode is on. This avoids repeated network
errors when the pool controller is disconnected for winter.
