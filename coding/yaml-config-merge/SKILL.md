---
name: yaml-config-merge
description: Reusable Python snippet for loading layered YAML config files (package defaults, then user, then project) where lists of objects merge by id or name instead of being replaced, and a disabled flag can switch off an inherited entry. Use when adding, reviewing, or refactoring layered or multi-file config loading in a Python project, copying the managed yaml-config-merge snippet into a repo, checking a repo's copy against the latest version, or deciding how config overrides should combine across scopes.
---

# Snippet: yaml-config-merge v1

Reusable function for merging layered YAML configs. Arrays of dicts are
automatically merged by composite identity key (from `id`, `name`, or
caller-specified fields). Scalars and plain lists are replaced by later layers.

## When to use

Any project that loads config from multiple YAML files (defaults + user
overrides) and needs arrays of objects merged by identity rather than replaced.

## Canonical Implementation

```python
# --- Reusable Snippet: yaml-config-merge v1 ---
# Managed by skill: yaml-config-merge
# Keep consistent with the latest version of this snippet.
# Do not modify without updating the skill definition.
# ------------------------------------------------
from __future__ import annotations

from pathlib import Path
import yaml


def merge_yaml_configs(
    paths: list[Path | str], key_fields: list[str] | None = None
) -> dict:
    """Load YAML files in order and deep-merge them (later layers win).

    Arrays of dicts are merged by composite identity built from key_fields
    (default: ['id', 'name']). Missing files are silently skipped.
    At least one file must exist.
    """
    key_fields = key_fields or ["id", "name"]
    merged: dict = {}
    found = False
    for path in paths:
        p = Path(path)
        if not p.exists():
            continue
        found = True
        with open(p) as f:
            layer = yaml.safe_load(f) or {}
        merged = _merge_dicts(merged, layer, key_fields)
    if not found:
        raise FileNotFoundError(f"No config files found in: {paths}")
    return merged


def _merge_dicts(base: dict, overlay: dict, key_fields: list[str]) -> dict:
    key = lambda item: "|".join(str(item.get(f, "")) for f in key_fields)
    result = dict(base)
    for field, value in overlay.items():
        existing = result.get(field)
        if isinstance(existing, dict) and isinstance(value, dict):
            result[field] = _merge_dicts(existing, value, key_fields)
        elif (
            isinstance(existing, list)
            and isinstance(value, list)
            and existing
            and isinstance(existing[0], dict)
        ):
            merged = {key(obj): dict(obj) for obj in existing}
            for obj in value:
                k = key(obj)
                if k in merged:
                    merged[k].update(obj)
                else:
                    merged[k] = dict(obj)
            result[field] = list(merged.values())
        else:
            result[field] = value
    return result
```

## Usage

### Entries matched by `name` (e.g. a list of bills or accounts)

```python
from myapp.sdk.common.yaml_merge import merge_yaml_configs

config = merge_yaml_configs([package_defaults_path, user_config_path])
# Entry lists merged by name. Filter entries marked deleted/disabled afterwards.
```

### Entries matched by `id` (e.g. rules or patterns)

```python
from myapp.sdk.common.yaml_merge import merge_yaml_configs

config = merge_yaml_configs([system_defaults_path, *bundle_paths, user_config_path])
# Entry lists merged by id. Apply enable/disable flags afterwards.
```

### Another identity field

```python
config = merge_yaml_configs(paths, key_fields=["pattern"])
```

## Placement

Copy into each consuming repo at `<package>/sdk/common/yaml_merge.py`
or similar utility module.

## Version History

- **v1**: Extracted from two projects' config loaders. Single public function, auto-detects list-of-dict arrays,
  composite identity key from configurable fields.
