#!/usr/bin/env python3
"""Package a compiled NavPad telemetry Backpack OTA image. Does not flash."""

import argparse
import gzip
import io
import json
from pathlib import Path
import sys

import zopfli.gzip


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("upstream", type=Path, help="Pinned ExpressLRS Backpack source directory")
    parser.add_argument("stock_pocket", type=Path, help="Known-good Pocket Backpack 1.5.7 OTA image")
    parser.add_argument("output", type=Path, help="New .bin.gz file")
    args = parser.parse_args()

    sys.path.insert(0, str(args.upstream.resolve() / "python"))
    from UnifiedConfiguration import findFirmwareEnd

    stock = gzip.decompress(args.stock_pocket.read_bytes())
    build = args.upstream / ".pio/build/ESP_TX_Backpack_via_WIFI/firmware.bin"
    image = build.read_bytes()
    target_marker = b"\xbe\xef\xca\xfeESP_TX_BACKPACK\0"
    for payload in (stock, image):
        if payload[:2] != b"\xe9\x02" or payload[0x1000] != 0xE9 or target_marker not in payload:
            parser.error("Both images must target the ESP8285 TX Backpack.")
    routes = (b"/navpad/gps\0", b"/navpad/telemetry\0", b"/navpad/telemetry/v3\0")
    if any(route not in image for route in routes):
        parser.error("The new image is missing a NavPad telemetry endpoint.")

    stock_end = findFirmwareEnd(io.BytesIO(stock))
    options = stock[stock_end:stock_end + 513]
    decoded = json.loads(options.split(b"\0", 1)[0])
    if decoded.get("product-name") != "RadioMaster Pocket Internal 2.4GHz TX" or len(options) != 513:
        parser.error("The reference image must contain the exact RadioMaster Pocket identity.")
    image_end = findFirmwareEnd(io.BytesIO(image))
    if not 0x1000 < image_end <= len(image):
        parser.error("The firmware boundary is outside the new image.")
    packaged = image[:image_end] + options
    compressed = zopfli.gzip.compress(packaged)
    if gzip.decompress(compressed) != packaged:
        parser.error("The compressed image failed round-trip validation.")
    with args.output.open("xb") as output:
        output.write(compressed)
    print(f"Verified {args.output.name}: {len(compressed)} bytes, RadioMaster Pocket ESP8285")


if __name__ == "__main__":
    main()
