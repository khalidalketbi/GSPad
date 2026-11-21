# GSPad HTTP telemetry interface

GSPad reads telemetry from a compatible Pocket Backpack over its local Wi-Fi network. Install the [Pocket Telemetry v3 firmware](../updates/README.md) to provide the HTTP routes documented here.

The API retains the `/navpad/` path and `X-NavPad-Backpack` header from the earlier project name. These names are part of the existing protocol.

## Read a response

Join the Backpack's **telemetry** network, then run:

```sh
curl -i --max-time 5 http://10.0.0.1/navpad/telemetry/v3
```

All three routes are read-only:

| Route | `X-NavPad-Backpack` | Body format |
| --- | --- | --- |
| `/navpad/telemetry/v3` | `3` | One `<hex>;<age_ms>;<sequence>` line per frame. |
| `/navpad/telemetry` | `2` | One hexadecimal packet per line, without capture metadata. |
| `/navpad/gps` | `1` | GPS packets only, in hexadecimal, without capture metadata. |

The hexadecimal field is the full **MSPv2 packet containing a CRSF frame**. It is not a JSON object or a raw latitude/longitude pair. Decode the hex and validate the MSPv2 and CRSF checksums before using the payload.

For v3, split each non-empty line at the two semicolons:

- **`hex`**: lowercase hexadecimal packet bytes.
- **`age_ms`**: unsigned decimal age in milliseconds, measured when the Backpack generates the response.
- **`sequence`**: unsigned 32-bit capture counter. It increments on each captured frame, including a repeated payload, and wraps after `4294967295`.

Polling again can return a cached frame with the same sequence and a greater age. Treat it as the same captured frame rather than another telemetry sample. With v1/v2, identical payloads cannot establish that a new capture occurred.

## Status and freshness

| HTTP status | Meaning |
| --- | --- |
| `200` | One or more fresh cached frames are available. |
| `204` | There are no fresh frames for the selected route. |
| `503` | The Backpack is not in the required access-point Wi-Fi telemetry mode, or it could not construct a response. |

Responses use **`Cache-Control: no-store`**. The firmware keeps up to **24 frame type/source pairs**, replaces a pair when a new frame arrives, and omits frames older than **2500 ms**. It provides recent state rather than a lossless packet history.

Available frame families include GPS, barometer, vario, attitude, battery, flight mode, link statistics, airspeed, RPM, temperature, voltages, and GPS home. Their presence depends on the aircraft, sensors, and radio forwarding those frames.

## Reference implementation

- [Firmware patch](../firmware/backpack-1.5.7/navpad-direct-gps.patch): frame capture, cache, routes, status codes, and response headers.
- [Pinned Backpack source and build guide](../firmware/backpack-1.5.7/README.md).
- [Pinned CRSF specification](https://github.com/tbs-fpv/tbs-crsf-spec/blob/a73f7dc5386e5b8744aa4a23b3af5354ee0d4c92/crsf.md).

The custom firmware keeps the original upstream CRSF broadcast available. The App Store version's documented connection path uses HTTP. These endpoints do not configure or control the aircraft.
