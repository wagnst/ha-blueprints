"""Validate all blueprint YAML files in the repository.

Checks that every automations/**/*.yaml file parses as YAML (including the
Home Assistant specific !input tag) and contains the mandatory blueprint
keys.
"""

import glob
import sys

import yaml


class BlueprintLoader(yaml.SafeLoader):
    """SafeLoader that tolerates Home Assistant's !input tag."""


def _construct_input(loader: BlueprintLoader, node: yaml.Node) -> dict:
    return {"__input__": loader.construct_scalar(node)}


BlueprintLoader.add_constructor("!input", _construct_input)


def main() -> int:
    paths = sorted(glob.glob("automations/**/*.yaml", recursive=True))
    if not paths:
        print("No blueprint files found under automations/")
        return 1

    failed = False
    for path in paths:
        try:
            with open(path, encoding="utf-8") as handle:
                data = yaml.load(handle, Loader=BlueprintLoader)
        except yaml.YAMLError as exc:
            print(f"FAIL {path}: invalid YAML: {exc}")
            failed = True
            continue

        blueprint = (data or {}).get("blueprint")
        if not isinstance(blueprint, dict):
            print(f"FAIL {path}: missing 'blueprint' section")
            failed = True
            continue

        missing = [key for key in ("name", "domain") if not blueprint.get(key)]
        if missing:
            print(f"FAIL {path}: missing blueprint keys: {', '.join(missing)}")
            failed = True
            continue

        print(f"OK   {path}: {blueprint['name']} ({blueprint['domain']})")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
