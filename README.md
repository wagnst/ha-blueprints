# ha-blueprints

A collection of [Home Assistant](https://www.home-assistant.io/) blueprints.

Each blueprint consists of a `.yaml` file with the actual blueprint code and
a `.md` file next to it with setup and usage documentation.

## How to import a blueprint

Click the *Import Blueprint* badge of the blueprint you want to use — it
opens your own Home Assistant instance with the import dialog pre-filled
(requires [My Home Assistant](https://my.home-assistant.io/)). Alternatively,
go to **Settings → Automations & Scenes → Blueprints → Import Blueprint** in
Home Assistant and paste the blueprint's import URL.

After importing, create a new automation from the blueprint and fill in its
inputs.

## Versioning and updates

Every merged change to a blueprint automatically creates a
[GitHub release](https://github.com/wagnst/ha-blueprints/releases). The import badges point at the latest
release, so importing — or re-importing — always installs the newest
version. Home Assistant does not update imported blueprints on its own: to
update, open **Settings → Automations & Scenes → Blueprints**, click the
three-dot menu on the blueprint and choose **Re-import blueprint**.

## Automation blueprints

### [Sync Two Covers](automations/sync_two_covers.md)

Keeps two covers (e.g. roller shutters) in sync, bidirectionally. When
either cover opens, closes or stops — via wall button, UI or service call —
the other one mirrors it, including the exact position. Built-in loop
protection, no helper entities required.

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fwagnst%2Fha-blueprints%2Freleases%2Flatest%2Fdownload%2Fsync_two_covers.yaml)

[Code](automations/sync_two_covers.yaml) · [Documentation](automations/sync_two_covers.md)

## License

[MIT](LICENSE)
