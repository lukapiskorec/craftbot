"""Above-camera roof-on/off presentation series using viewer layers."""

from pathlib import Path

import layers


PRESENTATION_ABOVE = True
path = Path(layers.__file__).with_name("views_cycles_layer_series.py")
exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"))
