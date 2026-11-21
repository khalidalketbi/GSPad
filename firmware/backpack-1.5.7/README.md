# GSPad / NavPad Telemetry v3 for RadioMaster Pocket

`Pocket-Backpack-1.5.7-Stock.bin.gz` contains the [official 1.5.7 generic ESP TX Backpack program](https://expresslrs.github.io/web-flasher/assets/backpack/6ca4b77a12610d76a1f1fae7e9eb5a559324d5fc/ESP_TX_Backpack/firmware.bin) configured for the RadioMaster Pocket ELRS ESP8285 target, with no binding phrase or home-network credentials. It is provided for manual upgrade from older releases that cannot report a Pocket-specific identity. Check the radio model before selecting the stock file on its Backpack update page. If the stock updater reports insufficient space, use the [official EdgeTX Passthrough procedure](https://www.expresslrs.org/hardware/backpack/backpack-tx-setup/) with the Pocket target.

The ESP8285 TX Backpack image is based on [ExpressLRS Backpack 1.5.7](https://github.com/ExpressLRS/Backpack/releases/tag/1.5.7), commit `6ca4b77a12610d76a1f1fae7e9eb5a559324d5fc`. The patch and [GPLv3 license](LICENSE) accompany this image. The complete pinned upstream source is included as [Upstream/Backpack-6ca4b77.tar.gz](Upstream/Backpack-6ca4b77.tar.gz), with its digest in [SHA256SUMS](SHA256SUMS). The patch and packaging script in this directory supply the modifications and packaging instructions. See the [manual update guide and verification status](../../updates/README.md) before using the binaries.

In the Backpack access point and Wi-Fi telemetry mode, `GET http://10.0.0.1/navpad/telemetry/v3` returns one `<hex>;<age_ms>;<seq>` line per cached frame, marked `X-NavPad-Backpack: 3`. The age is measured at the time the Backpack generates the response. The unsigned 32-bit sequence advances on capture, including when a newly captured payload is identical, and wraps at its limit. The firmware keeps at most 24 recent frame type/source pairs for GPS, barometer, vario, attitude, battery, flight mode, link statistics, airspeed, RPM, temperature, voltages and GPS home. Responses carry `Cache-Control: no-store`. Frames older than 2.5 seconds are omitted. No fresh frames returns 204 and an unsupported Backpack mode returns 503.

The older `/navpad/telemetry` (version 2) and `/navpad/gps` (version 1) keep their original hexadecimal bodies. All three endpoints are read-only, and the original CRSF broadcast remains available. NavPad validates both checksums and tries the older routes when the newer route is absent. With version 1 or 2, identical payloads cannot prove a new capture. NavPad reports age since the last changed payload in this mode.

Telemetry mode skips captive portal probe handlers, wildcard DNS and HTTP redirects to the ExpressLRS page. The dedicated firmware update mode retains the upstream portal behavior. The Pocket network may still be reported by the iPad as having no internet.

The app's field decoding follows [the pinned CRSF specification](https://github.com/tbs-fpv/tbs-crsf-spec/blob/a73f7dc5386e5b8744aa4a23b3af5354ee0d4c92/crsf.md) and the frames produced by [INAV 7.1.2](https://github.com/iNavFlight/inav/blob/7.1.2/src/main/telemetry/crsf.c) and [INAV 9.1.0](https://github.com/iNavFlight/inav/blob/9.1.0/src/main/telemetry/crsf.c). The TX module [in ELRS 3.6.4](https://github.com/ExpressLRS/ExpressLRS/blob/b61c9e24305b2f80046a5e0b3c4edf56c4f059a3/src/src/tx_main.cpp) also forwards the link statistics packet to the Backpack. Displayed data depends on the sensors and frame types sent by the specific aircraft and radio.

## Build a local test image

Run from the root of a clone of this GSPad repository. The build directory stays inside the clone. Use a new build directory each time; the initial check refuses to reuse one. The Git checkout provides upstream version stamping; the included archive supplies the pinned source for inspection.

```sh
set -eu
gspad_root="$PWD"
STOCK_POCKET_OTA="$gspad_root/firmware/backpack-1.5.7/Pocket-Backpack-1.5.7-Stock.bin.gz"
pocket_build="$gspad_root/.firmware-build"
test ! -e "$pocket_build" || exit 1
mkdir -p "$pocket_build"
git clone --depth 1 --branch 1.5.7 https://github.com/ExpressLRS/Backpack.git "$pocket_build/upstream"
test "$(git -C "$pocket_build/upstream" rev-parse HEAD)" = 6ca4b77a12610d76a1f1fae7e9eb5a559324d5fc
git -C "$pocket_build/upstream" apply "$gspad_root/firmware/backpack-1.5.7/navpad-direct-gps.patch"
python3 -m venv "$pocket_build/venv"
"$pocket_build/venv/bin/pip" install platformio==6.1.19 zopfli==0.4.1
PLATFORMIO_CORE_DIR="$pocket_build/pio" "$pocket_build/venv/bin/pio" run -d "$pocket_build/upstream" -e ESP_TX_Backpack_via_WIFI
"$pocket_build/venv/bin/python" "$gspad_root/firmware/backpack-1.5.7/package.py" \
  "$pocket_build/upstream" "$STOCK_POCKET_OTA" "$pocket_build/Pocket-Backpack-1.5.7-NavPad-Telemetry-v3.bin.gz"
```

The packaging step checks the ESP8285 TX Backpack image marker, the Pocket product identity in the stock reference, and all three routes. It copies the reference image's embedded options and verifies the compressed image by decompressing it. [SHA256SUMS](SHA256SUMS) identifies the distributed artifacts in this directory. A fresh build may have a different digest depending on the toolchain and build environment. The commands build a file and do not upload it. Use the TX Backpack updater and the compressed file for the hardware test. Keep the aircraft off during the update and retain the known-good stock OTA image for rollback.

## Verify downloads

From this directory on macOS or Linux, run:

```sh
shasum -a 256 -c SHA256SUMS
```

The original `NavPad` filenames and protocol paths are retained for compatibility with GSPad. The binaries are distributed unchanged. Both images contain only generic Pocket identity options (`product-name` and `flash-discriminator`), with no user binding UID or home-network credentials.
