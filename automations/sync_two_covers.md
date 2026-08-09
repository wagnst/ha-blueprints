# Sync Two Covers

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fwagnst%2Fha-blueprints%2Freleases%2Flatest%2Fdownload%2Fsync_two_covers.yaml)

Questions or feedback? Join the
[community forum topic](https://community.home-assistant.io/t/sync-two-covers-keep-two-roller-shutters-perfectly-in-sync-bidirectional-loop-safe/1020570).

Keeps two covers (e.g. roller shutters) in sync, **bidirectionally**. No
matter which of the two covers is controlled — a wall button (e.g. a Shelly
input), the Home Assistant UI, a voice assistant or a service call — the
other cover always mirrors the movement:

- One cover starts **opening** → the other one opens too.
- One cover starts **closing** → the other one closes too.
- One cover **stops** (button pressed again, or end position reached) → the
  other one is driven to the **same position** and stops there (or is simply
  stopped, see *Exact position sync* below).

A typical use case: two shutters in the same room, each wired to its own
physical button, that should always behave as one.

No template cover, helper entities or extra automations are needed — one
automation created from this blueprint handles both directions.

## Requirements

- Both covers must be available as `cover` entities in Home Assistant and
  report their movement state (`opening` / `closing`). Shelly devices in
  cover/roller mode do this out of the box.
- For **exact position sync**, both covers must report and accept positions
  (0–100). On Shellys this requires the cover to be **calibrated** in the
  device settings. If your covers are not calibrated, disable the
  *Exact position sync* input — the follower is then stopped as soon as the
  controlled cover stops, which keeps them roughly in sync.

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| First cover | yes | – | One of the two covers to keep in sync. |
| Second cover | yes | – | The other cover to keep in sync. |
| Exact position sync | no | on | When one cover stops, let the other one continue to the exact same position instead of stopping it immediately. Requires calibrated (position-capable) covers. |

## How it works

The automation triggers on every state change of either cover to `opening`,
`closing`, `open` or `closed` and then applies three rules, where *source*
is the cover that changed and *target* is the other one:

1. Source started **opening** and the target is not already opening (and not
   fully open) → `cover.open_cover` on the target.
2. Source started **closing** and the target is not already closing (and not
   fully closed) → `cover.close_cover` on the target.
3. Source **stopped** (went from `opening`/`closing` to `open`/`closed`)
   while the target is still moving → the target is sent to the source's
   position with `cover.set_cover_position` if that only means *continuing*
   its current travel; otherwise (target already at or past the source's
   position, positions unavailable, or position sync disabled) the target is
   simply stopped with `cover.stop_cover`.

### Loop protection

Synchronizing two entities in both directions normally risks an infinite
feedback loop (A moves B, B's state change moves A, …). This blueprint
stacks three mechanisms, and still needs no helper entities:

- **Mirror commands are only sent when the target is not already doing the
  same thing.** When cover B starts opening because this automation told it
  to, B's own state change triggers the automation again — but its target
  (cover A) is already opening, so nothing happens.
- **A position command never reverses the follower.** Rule 3 only uses
  `cover.set_cover_position` when the follower keeps moving in its current
  direction. A reversal would emit a genuine `opening`/`closing` state that
  is indistinguishable from a button press and would be mirrored back —
  the classic ping-pong loop. If the follower has already passed the
  source's position it is stopped instead, which can leave the two covers a
  few percent apart (they re-align on the next full open/close). Rule 3
  also only ever touches a cover that is *currently moving* — a stationary
  cover is never "nudged".
- **A 2-second echo guard on the mirror rules.** After the automation has
  commanded a cover, movement state changes within the next 2 seconds are
  treated as echoes of that command and are not mirrored back. Only runs
  that actually command a cover count for this window, so it does not
  extend itself. Side effect worth knowing: a *contradictory* button press
  on the other cover within 2 seconds of a sync command is not mirrored —
  each cover then does its own thing until the next command re-syncs them.

State changes from or to `unavailable`/`unknown` (Home Assistant restarts,
devices dropping off the network) are ignored.

## Updating the blueprint

Every merged change to this blueprint automatically creates a
[GitHub release](https://github.com/wagnst/ha-blueprints/releases), and the
import URL always points at the latest release. Imported blueprints still do **not** update automatically in
Home Assistant, though: to get the newest version, open
**Settings → Automations & Scenes → Blueprints**, click the three-dot menu
on *Sync Two Covers* and choose **Re-import blueprint**. Existing
automations pick up the new logic immediately after the re-import.

## Testing checklist

After creating the automation, verify the behavior:

1. Press **up** on one shutter's button → both shutters open.
2. Press **stop** mid-travel → both shutters stop at (about) the same
   position.
3. Press **down** on the *other* shutter's button → both shutters close.
4. Move one shutter from the Home Assistant UI, including the position
   slider → the other follows and settles at the same position.

## Troubleshooting

- **The follower does not stop at the same position** — check that both
  covers are calibrated and show a `current_position` attribute. Without
  positions the blueprint falls back to a plain stop, and differing motor
  speeds can cause drift.
- **Nothing happens at all** — check the automation's trace in Home
  Assistant (Settings → Automations → your automation → Traces). If the
  trigger never fires, the cover integration may not report
  `opening`/`closing` states. Note that traces only show runs that actually
  commanded a cover; ignored echoes and no-op events are filtered out by the
  automation's conditions and don't appear.
- **A button press on the second cover is ignored** — presses within 2
  seconds of the last sync command fall into the echo guard window (see
  *Loop protection*) and are deliberately not mirrored. Press again a
  moment later.
- **Covers move on Home Assistant restart** — they shouldn't: transitions
  involving `unavailable`/`unknown` are filtered out. If you see this,
  please open an issue with the automation trace attached.
