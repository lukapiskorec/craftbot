"""Map exterior wall skin names and positions to cardinal facades."""

import re


_SIGNED_AXIS = (
    ("south", r"(?:neg(?:ative)?|minus)_?y|y_?(?:neg(?:ative)?|minus)"),
    ("north", r"(?:pos(?:itive)?|plus)_?y|y_?(?:pos(?:itive)?|plus)"),
    ("west", r"(?:neg(?:ative)?|minus)_?x|x_?(?:neg(?:ative)?|minus)"),
    ("east", r"(?:pos(?:itive)?|plus)_?x|x_?(?:pos(?:itive)?|plus)"),
)


def facade_hint(text):
    """Return a cardinal facade encoded in a collection/name, if unambiguous."""
    normalized = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    padded = f"_{normalized}_"
    matches = []
    for facade in ("south", "north", "west", "east"):
        if re.search(rf"(?:^|_){facade}(?:_|$)", normalized):
            matches.append(facade)
    for facade, pattern in _SIGNED_AXIS:
        if re.search(rf"(?:^|_)(?:{pattern})(?:_|$)", normalized):
            matches.append(facade)
    for token, facade in (("s", "south"), ("n", "north"), ("w", "west"), ("e", "east")):
        if f"_{token}_" in padded:
            matches.append(facade)
    unique = list(dict.fromkeys(matches))
    return unique[0] if len(unique) == 1 else None


def facade_for(text, center_xy, bounds_xy):
    """Use a semantic hint, then choose the nearest normalized XY boundary."""
    hinted = facade_hint(text)
    if hinted:
        return hinted
    x, y = center_xy
    xmin, xmax, ymin, ymax = bounds_xy
    xspan = max(xmax - xmin, 1e-9)
    yspan = max(ymax - ymin, 1e-9)
    distances = {
        "west": abs(x - xmin) / xspan,
        "east": abs(xmax - x) / xspan,
        "south": abs(y - ymin) / yspan,
        "north": abs(ymax - y) / yspan,
    }
    return min(distances, key=distances.get)
