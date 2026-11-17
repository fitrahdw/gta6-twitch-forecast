"""Leave-one-out backtest for main.py's forecaster, over the comparables.

The kit publishes no practice answers (each practice case's release-day
hours are the server's scorer data, and no case holds another case's
answer), so the honest local ground truth is the comparables themselves:
each comparable is a fully observed past launch. For every usable
comparable this script pretends it is an unseen launch -- hour 1 known,
hours 2..24 to forecast -- builds main.py's template from the *other*
comparables, and scores the result with the contest's own rule (mean
pinball loss on the log scale), next to the house persistence baseline on
the same launch.

Usage: python3 backtest.py <kit-input-dir>   (the dir holding p00.in..p03.in)
"""

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import main as entry

LEVELS = entry.LEVELS
Z = entry.Z


def pinball(forecast_log_q: dict, actual_log_ratio: dict) -> float:
    total, n = 0.0, 0
    for h, ly in actual_log_ratio.items():
        for tau, lq in zip(LEVELS, forecast_log_q[h]):
            d = ly - lq
            total += 2 * max(tau * d, (tau - 1) * d)
            n += 1
    return total / n


def comparable_as_target(case: dict, comp: dict) -> tuple[dict, dict]:
    """Split one comparable into (a pseudo-case carrying the others, the
    target's actual log ratios for hours 2..24)."""
    others = [c for c in case["comparables"] if c is not comp]
    pseudo = {"game": {"name": "__held_out__"}, "comparables": others, "notes": comp.get("unlock", "")}
    day_start = entry.parse_time(comp["day_start"])
    by_hour = {}
    for point in comp["hourly"]:
        offset = (entry.parse_time(point["from"]) - day_start).total_seconds() / 3600.0
        if offset == int(offset) and 0 <= int(offset) <= 23 and point["viewers"]:
            by_hour[int(offset) + 1] = float(point["viewers"])
    if 1 not in by_hour:
        return pseudo, {}
    actual = {h: math.log(v / by_hour[1]) for h, v in by_hour.items() if h >= 2}
    return pseudo, actual


def main() -> None:
    kit_input = Path(sys.argv[1])
    case = json.loads((kit_input / "p00.in").read_text(encoding="utf-8"))
    rows = []
    a_flags = []
    for comp in case["comparables"]:
        pseudo, actual = comparable_as_target(case, comp)
        shapes = entry.comparable_shapes(pseudo)
        if len(actual) < 20 or len(shapes) < entry.MIN_COMPARABLES:
            continue
        day_start = entry.parse_time(comp["day_start"])
        day = {}
        for point in comp["hourly"]:
            offset = (entry.parse_time(point["from"]) - day_start).total_seconds() / 3600.0
            if offset == int(offset) and 0 <= int(offset) <= 23 and point["viewers"]:
                day[int(offset) + 1] = float(point["viewers"])
        a_flags.append(day[1] / max(day.values()) >= 0.15)
        template = entry.shape_template(shapes)
        if entry.is_global_unlock(pseudo):
            shrink, ss = entry.SHRINK_GLOBAL, entry.SPREAD_SCALE_GLOBAL
        else:
            shrink, ss = entry.SHRINK, entry.SPREAD_SCALE
        ours = {h: [entry.SHIFT + shrink * template[h] + z * ss * 0.15 * math.sqrt(h - 1) for z in Z]
                for h in actual}
        base = {h: [z * 0.15 * math.sqrt(h - 1) for z in Z] for h in actual}
        rows.append((comp["name"], pinball(ours, actual), pinball(base, actual)))
    ours_mean = sum(r[1] for r in rows) / len(rows)
    base_mean = sum(r[2] for r in rows) / len(rows)
    for name, ours_s, base_s in rows:
        print(f"{name[:44]:46s} ours {ours_s:.4f}  baseline {base_s:.4f}")
    print(f"\n{len(rows)} launches  ours {ours_mean:.4f}  baseline {base_mean:.4f}")
    # The subsets that resemble this bounty (rolling midnight console
    # launches whose hour 1 already holds a large share of the day's peak)
    # are the forecast's real reference class; print them separately.
    a_rows = [(o, b) for (name, o, b), a in zip(rows, a_flags) if a]
    if a_rows:
        print(f"  of which already-launched-by-hour-1: ours "
              f"{sum(o for o, _ in a_rows) / len(a_rows):.4f}  baseline "
              f"{sum(b for _, b in a_rows) / len(a_rows):.4f}  (n={len(a_rows)})")


if __name__ == "__main__":
    main()
