"""Compatibility name for the layer-driven four-view presentation series."""

from pathlib import Path

import layers


path = Path(layers.__file__).with_name("views_cycles_layer_series.py")
exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"))
