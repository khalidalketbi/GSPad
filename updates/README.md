# GSPad telemetry: downloads and updates

This package adds the local HTTP telemetry interface that GSPad reads over Wi-Fi. It is **ExpressLRS Backpack 1.5.7 + GSPad/NavPad Telemetry v3**, for the **ESP8285 TX Backpack in the RadioMaster Pocket Internal 2.4GHz TX**.

The App Store edition of GSPad uses compatible firmware already installed on the Backpack. Install these files through the Backpack's web update page.

## Choose the right file

| Download | Purpose |
| --- | --- |
| [Telemetry v3 `.bin.gz`](https://raw.githubusercontent.com/khalidalketbi/GSPad/main/firmware/backpack-1.5.7/Pocket-Backpack-1.5.7-NavPad-Telemetry-v3.bin.gz) | Modified Backpack 1.5.7 with the HTTP telemetry endpoints needed by GSPad. |
| [Stock 1.5.7 `.bin.gz`](https://raw.githubusercontent.com/khalidalketbi/GSPad/main/firmware/backpack-1.5.7/Pocket-Backpack-1.5.7-Stock.bin.gz) | Pocket-configured stock program for a legacy upgrade or rollback. It does not provide the custom HTTP endpoints. |
| [SHA256SUMS](../firmware/backpack-1.5.7/SHA256SUMS) | Check the two firmware downloads before selecting them in the updater. |
| [Source and build guide](../firmware/backpack-1.5.7/README.md) | Upstream source archive, patch, packaging script, license, and build instructions. |

Keep the firmware files compressed as **`.bin.gz`**. The source `.tar.gz` archive is for developers and is not an update file.

## Check the target first

These are **Pocket ESP8285 TX Backpack** images. Confirm your radio and Backpack hardware before uploading. The Pocket's RF transmitter has a separate updater and firmware. Its Wi-Fi network is called **ExpressLRS TX**; use the **TX Backpack** update network for this package.

If a legacy Backpack cannot identify the Pocket correctly, verify the physical model and use the stock upgrade path below. Do not override a target mismatch.

## Install through the Backpack web page

1. Download the files and instructions while you have internet. Keep the aircraft powered off and maintain reliable power to the Pocket during the update.
2. On the Pocket, open **SYS → TOOLS → ExpressLRS → WiFi Connectivity → Enable Backpack WiFi**.
3. Join the **ExpressLRS TX Backpack** update network on your iPhone, iPad, or computer. The telemetry-mode network may include a device suffix. If asked, choose **Without Internet** to stay connected.
4. Open **http://10.0.0.1** in a browser. Confirm that it is the **Backpack** update page and check the device identity and firmware version.
5. If you are upgrading an older Backpack such as 1.3.0, first select the **Stock 1.5.7** `.bin.gz` file with **Choose File**, then select **Update**. Let the Backpack restart. Re-enable **WiFi Connectivity → Enable Backpack WiFi**, rejoin the **unsuffixed update network**, and reopen **http://10.0.0.1**. Verify **1.5.7 (6ca4b7)** and the matching Pocket identity before continuing.
6. On the matching Pocket Backpack running 1.5.7, select the **NavPad Telemetry v3** `.bin.gz` file and select **Update**. Let the Backpack restart before changing modes or disconnecting power.
7. If the updater reports a target mismatch or **Not Enough Space**, stop this upload path and follow the [official Backpack setup/recovery instructions](https://www.expresslrs.org/hardware/backpack/backpack-tx-setup/) for the exact Pocket target and **EdgeTXPassthrough**.

The filename retains the earlier **NavPad** project name. It is the GSPad-compatible HTTP telemetry firmware.

## Reconnect to GSPad

1. On the Pocket, use **Link Mode → Normal** and **Backpack → Telemetry → WiFi**.
2. Join the Backpack's telemetry Wi-Fi network, which may have a device suffix.
3. Open GSPad, allow **Local Network** access, and tap **Connect**. Use **Set Up Pocket** to check the connection and firmware.
4. The aircraft marker requires valid GPS telemetry from the aircraft. A successful connection can precede a GPS fix.

For a read-only check from a computer on that network:

```sh
curl -i --max-time 5 http://10.0.0.1/navpad/telemetry/v3
```

Look for **`X-NavPad-Backpack: 3`**. A **204** response means there are no fresh frames to return; **503** usually means that the required Wi-Fi telemetry mode is not active. See the [API details](../telemetry/README.md).

## If the radio has no Telemetry → WiFi menu

Check the RF transmitter's ExpressLRS version and Lua script using the [official RadioMaster internal TX guide](https://www.expresslrs.org/quick-start/transmitters/rm-internal/). The project used [ExpressLRS 3.6.4](https://github.com/ExpressLRS/ExpressLRS/releases/tag/3.6.4) as a pinned reference; it is not described here as the latest release.

Use the official tool to select the exact **RadioMaster Pocket Internal 2.4GHz TX** target, the appropriate regulatory domain, and your existing binding configuration. Generic TX application images require device-specific assembly, so this package supplies the ready-to-select **Backpack** files above.

## Verification status

Firmware build, packaging, hashes, and HTTP integration were verified in the project records. Partial hardware testing confirmed Pocket identity, Backpack 1.5.7, and HTTP telemetry v3 connectivity. Complete aircraft telemetry/GPS and this exact OTA flashing path have not been fully verified on physical hardware. This publication preserves those existing firmware bytes and adds documentation; it does not claim a new hardware test.

For the iPhone/iPad app itself, get updates through [GSPad on the App Store](https://apps.apple.com/us/app/gspad/id6832260857). Firmware package changes are listed in the [change log](../CHANGELOG.md).
