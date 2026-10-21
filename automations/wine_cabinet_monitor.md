# Wine Cabinet Monitor

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fwagnst%2Fha-blueprints%2Freleases%2Flatest%2Fdownload%2Fwine_cabinet_monitor.yaml)

Watches a wine cabinet (or any fridge, cellar or humidor) through its
temperature sensor and, optionally, its humidity sensor, and tells you when
storage conditions drift out of range:

- **Too warm / too cold** — a failed compressor, a door left open, a
  thermostat fault or a setpoint changed by mistake.
- **Too humid / too dry** — mouldy labels on one side, shrinking corks on
  the other.
- **Sensor offline** — a flat battery or Wi-Fi trouble means the cabinet is
  unmonitored, which is as bad as a warm cabinet you don't know about.
- **Too much temperature swing** over 24 hours (optional) — stability harms
  wine more than a slightly wrong absolute temperature.

Every alert has a **duration guard**, so the normal ±1 °C compressor
cycling, a door opened to fetch a bottle, or a dozen room-temperature
bottles loaded at once never page you. Every alert is followed by a
**recovery message** once conditions are back in range, and alerts are
shown as **persistent notifications** in Home Assistant that are dismissed
automatically on recovery — the notification drawer always reflects the
cabinet's current state.

A typical setup: a Shelly H&T (or any temperature/humidity sensor) placed
mid-height on a shelf of a compressor wine cabinet, one automation per
cabinet, notifications to your phone.

## Requirements

- A temperature `sensor` entity with device class `temperature`.
- Optionally a humidity `sensor` with device class `humidity`.
- Optionally, for the swing check, a **statistics helper** on the
  temperature sensor — see *Temperature swing* below.
- Home Assistant 2024.10 or newer.

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| Cabinet name | no | Wine cabinet | Used in notification titles and messages. One automation per cabinet — give each its own name. |
| Temperature sensor | yes | – | The cabinet's temperature sensor. |
| Humidity sensor | no | – | The cabinet's humidity sensor. Leave empty to skip humidity monitoring. |
| **Temperature limits** | | | |
| Too warm above | no | 16 °C | Alert when the temperature stays above this. Wine is stored at 10–14 °C; 16 °C catches real faults without reacting to cycling. |
| Too cold below | no | 8 °C | Alert when the temperature stays below this. |
| Temperature alert delay | no | 60 min | How long the temperature must stay out of range before an alert is sent. |
| **Humidity limits** | | | |
| Too humid above | no | 78 % | 50–70 % is ideal; above ~75 % for weeks labels start to mould. |
| Too dry below | no | 45 % | Compressor cabinets run dry; below ~45 % for long periods corks can shrink. |
| Humidity alert delay | no | 1440 min (24 h) | Humidity only matters over days. |
| **Temperature swing** | | | |
| Temperature swing sensor | no | – | A statistics helper giving max − min of the temperature over 24 h. Leave empty to skip. |
| Maximum swing | no | 3 K | Alert when the 24-hour swing exceeds this. |
| **Notifications** | | | |
| Notification actions | no | – | Actions to run for every alert and recovery (see below). |
| Also notify when back to normal | no | on | Send recovery messages through the notification actions. Persistent notifications are always dismissed on recovery. |
| Show alerts as persistent notifications | no | on | One persistent notification per alert type, dismissed on recovery. |
| Sensor offline delay | no | 30 min | Alert when the temperature sensor has been `unavailable`/`unknown` this long. |

### Notification actions

The *Notification actions* input takes any list of actions. Inside them the
variables `title` and `message` hold the ready-made text, so a mobile
notification is just:

```yaml
action: notify.mobile_app_your_phone
data:
  title: "{{ title }}"
  message: "{{ message }}"
```

Add a second action for a second phone, a TTS announcement, a Telegram
message — anything. Leave the input empty if the persistent notifications
in Home Assistant are enough.

Messages look like:

> **Garage cabinet A: alert** — Temperature is 17.2 °C — above 16 °C for
> more than 60 minutes. Check the door and whether the compressor is
> running.

> **Garage cabinet A: back to normal** — Temperature is back in range at
> 13.4 °C.

### Temperature swing (optional)

Home Assistant templates cannot look at history, so the swing check uses a
statistics helper you create once per cabinet:

1. **Settings → Devices & services → Helpers → Create helper → Statistics**
2. Input sensor: the cabinet's temperature sensor
3. Characteristic: **Distance (absolute)** — the difference between the
   largest and smallest value
4. Max age: **24 hours** (leave *sampling size* empty, or large)
5. Name it e.g. `Garage cabinet A temperature swing 24h`

Then select that helper as *Temperature swing sensor*. A healthy cabinet
stays within 2–3 K over a day; a larger swing means the door is opened too
often, the room's temperature swings a lot (garage in summer) or the
cabinet is undersized for the room.

## How it works

Every check is a pair of triggers with an id — an *alert* trigger with a
long `for:` and a *recovery* trigger with a short one:

| Check | Alert fires when … | Recovery fires when … |
| --- | --- | --- |
| Temperature | above *Too warm* or below *Too cold* for *alert delay* | back between the two limits for 10 min |
| Humidity | above *Too humid* or below *Too dry* for *alert delay* | back between the two limits for 60 min |
| Sensor | `unavailable`/`unknown` for *offline delay* | any value again for 1 min |
| Swing | swing sensor above *Maximum swing* for 30 min | below it for 60 min |

The trigger id selects the message text; the recovery dismisses the
persistent notification of its own topic (temperature, humidity, sensor or
swing), so a humidity alert never hides a temperature alert.

Numeric triggers fire on *crossing* a threshold. Two consequences worth
knowing:

- A cabinet that is already out of range when Home Assistant starts (or
  when the automation is created) does not alert until the value crosses
  back in and out again. If you want to be sure, check the sensor once
  after setting things up.
- Likewise there is no recovery message at startup for a cabinet that is
  simply fine — recoveries only follow alerts.

The automation runs in `queued` mode, so a recovery arriving while an alert
is still being sent is never dropped.

## Updating the blueprint

Every merged change to this blueprint automatically creates a
[GitHub release](https://github.com/wagnst/ha-blueprints/releases), and the
import URL always points at the latest release. Imported blueprints still do
**not** update automatically in Home Assistant, though: to get the newest
version, open **Settings → Automations & Scenes → Blueprints**, click the
three-dot menu on *Wine Cabinet Monitor* and choose **Re-import blueprint**.
Existing automations pick up the new logic immediately after the re-import.

## Testing checklist

1. Temporarily set *Too warm above* to a value just below the current
   reading and *Temperature alert delay* to 1 minute → after a minute the
   alert arrives and a persistent notification appears.
2. Set the limit back → after 10 minutes in range the recovery arrives and
   the persistent notification disappears.
3. Pull the sensor's battery (or block it on your Wi-Fi) for longer than the
   *Sensor offline delay* → offline alert; put it back → "back online".
4. Check **Settings → Automations → your automation → Traces**: each run
   shows which trigger id fired.

## Troubleshooting

- **No alert although the cabinet is clearly too warm** — the value was
  probably already above the limit when the automation was created (see
  *How it works*). Let it drop below and rise again, or lower the limit
  briefly to force a crossing.
- **Alerts every hour from the same cabinet** — your limits are inside the
  cabinet's normal cycling band. A compressor cabinet cycles about ±1 K
  around the setpoint; keep *Too warm* at least 2 K above the setpoint, or
  lengthen the delay.
- **Humidity alerts straight after loading bottles** — new bottles and an
  open door raise humidity for a day or two; the 24 h default delay covers
  this. Shorter delays will fire.
- **Notification actions get an empty message** — make sure the action uses
  the variables `{{ title }}` and `{{ message }}` exactly as shown above;
  they are only defined inside this automation.
- **Shelly H&T reports rarely** — the H&T only wakes on a change (default
  0.5 °C / 5 %) or every few hours; that is fine for a cabinet, but a very
  short *alert delay* can't be shorter than the device's reporting
  interval in practice.
