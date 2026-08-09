# Sync Two Covers

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fwagnst%2Fha-blueprints%2Fblob%2Fmain%2Fautomations%2Fsync_two_covers.yaml)

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
| Exact position sync | no | on | When one cover stops, move the other one to the exact same position instead of just stopping it. Requires calibrated (position-capable) covers. |

## How it works

The automation triggers on every state change of either cover to `opening`,
`closing`, `open` or `closed` and then applies three rules, where *source*
is the cover that changed and *target* is the other one:

1. Source started **opening** and the target is not already opening (and not
   fully open) → `cover.open_cover` on the target.
2. Source started **closing** and the target is not already closing (and not
   fully closed) → `cover.close_cover` on the target.
3. Source **stopped** (went from `opening`/`closing` to `open`/`closed`)
   while the target is still moving → `cover.set_cover_position` on the
   target with the source's current position (or `cover.stop_cover` if
   position sync is off or positions are unavailable).

### Loop protection

Synchronizing two entities in both directions normally risks an infinite
feedback loop (A moves B, B's state change moves A, …). This blueprint
avoids that without helpers or timestamps:

- Mirror commands are only sent when the target is *not already doing the
  same thing*. When cover B starts opening because this automation told it
  to, B's own state change triggers the automation again — but its target
  (cover A) is already opening, so nothing happens.
- Rule 3 only ever touches a cover that is *currently moving*. When B is
  stopped at A's position, B's stop event triggers the automation again —
  but A is already stationary, so the chain always terminates. A stationary
  cover is deliberately never "nudged" to a new position, because that is
  exactly what would start a ping-pong loop.

State changes from or to `unavailable`/`unknown` (Home Assistant restarts,
devices dropping off the network) are ignored.

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
  `opening`/`closing` states.
- **Covers move on Home Assistant restart** — they shouldn't: transitions
  involving `unavailable`/`unknown` are filtered out. If you see this,
  please open an issue with the automation trace attached.
