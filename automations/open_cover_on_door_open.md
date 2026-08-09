# Open Cover on Door Open

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fwagnst%2Fha-blueprints%2Freleases%2Flatest%2Fdownload%2Fopen_cover_on_door_open.yaml)

Opens a cover when a door is opened. Typical use case: a balcony door with
a roller shutter — when you open the door to go outside, the shutter opens
automatically.

The automation is deliberately one-directional and conservative:

- It acts **only** on the door's closed → open transition, and **only** if
  the cover is not already fully open.
- While the door stays open, it never interferes. You can move the cover
  however you like — including fully down with the door open — and the
  automation will not fight you.
- Optionally it memorizes the cover's position at the moment the door
  opens and **restores** it after the door has been closed again — but
  only if the cover is still fully open at that moment. If you moved the
  cover while the door was open, your manual choice wins and nothing is
  restored.

No helper entities are required.

## Requirements

- A door contact exposed as a `binary_sensor` (`on` = open, `off` =
  closed), e.g. a Shelly Door/Window or any Zigbee/Z-Wave contact sensor.
- The cover as a `cover` entity. For restoring an exact position the cover
  must report and accept positions (e.g. a calibrated Shelly cover);
  covers without positions are restored by closing them if they were
  closed before.

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| Door sensor | yes | – | Binary sensor of the door (`on` = open). |
| Cover | yes | – | The cover to open when the door opens. |
| Restore the cover when the door is closed again | no | off | Memorize the cover's position when the door opens and restore it after the door has been closed — only if the cover is still fully open at that point. |
| Door-closed grace period | no | 10 s | How long the door must stay closed before the cover is restored. Reopening within this period keeps the cover open. |

## How it works

1. The door goes from closed to open. If the cover is already fully open
   (position ≥ 99, or state `open` for covers without positions) or
   unavailable, nothing happens at all.
2. Otherwise the cover's current position is memorized and the cover is
   opened.
3. With restoring enabled, the same automation run then waits: for the
   door to be closed, for it to *stay* closed for the grace period (going
   back to waiting if it is reopened), and for the cover to finish moving.
4. The memorized position is restored only if the door is still closed and
   the cover is still fully open. A cover that was moved while the door
   was open is left exactly where you put it.

## Safety design

- **No feedback loops possible.** The automation is triggered exclusively
  by the door sensor — never by the cover — so nothing it does to the
  cover can re-trigger it. It also composes safely with the
  [Sync Two Covers](sync_two_covers.md) blueprint: opening or restoring
  the cover simply syncs the partner cover along.
- **Manual control always wins.** While the door is open the automation is
  inert, and the restore step is skipped unless the cover is still exactly
  where the automation left it (fully open).
- **Door bouncing is absorbed.** One automation run handles the whole
  door-open "session" (`mode: single`): opening the door again while a
  session is active — including within the grace period — continues the
  session instead of starting a new one, so the cover is not cycled by
  quickly stepping in and out.
- **Restarts fail safe.** The door trigger requires an explicit
  closed → open transition, so Home Assistant restarts or a sensor
  recovering from `unavailable` never open the cover. The memorized
  position lives inside the running automation; if automations are
  reloaded or Home Assistant restarts while the door is open, the memory
  is forgotten and the cover simply stays open — it is never moved based
  on stale data.

While the door is open (with restoring enabled), the automation shows as
*running* in the UI — that is normal; the run is waiting for the door to
be closed.

## Testing checklist

1. Close the cover, then open the door → the cover opens.
2. With the door open, move the cover down → it stays down; close the
   door → it still stays down (manual choice wins).
3. Enable *Restore*: set the cover to e.g. 40 %, open the door → cover
   opens; close the door and wait out the grace period → cover returns
   to 40 %.
4. Open the door, close it, and reopen it within the grace period → the
   cover stays open the whole time.

## Troubleshooting

- **The cover doesn't open** — check that the door sensor reports `on`
  when open, and that the cover was not already fully open (nothing
  happens then by design).
- **The position is not restored** — restoring is skipped whenever the
  cover is no longer fully open (manual moves win), when the door was
  reopened, or when automations were reloaded / Home Assistant restarted
  during the door-open phase.
- **The automation shows as "running" for a long time** — expected while
  the door is open and restoring is enabled; the run ends after the door
  has been closed and the restore decision was made.
