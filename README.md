# gta6-twitch-forecast

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/fitrahdw/gta6-twitch-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/fitrahdw/gta6-twitch-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

Entry for make.fun's bounty "Forecast GTA VI's launch-day Twitch viewers hour by hour" (`gta6-twitch-ccu-forecast-01`, $250 USDC).

`main.py` (Python 3.13, standard library only) reads each case in `/input` and writes quantile forecasts (5%, 25%, 50%, 75%, 95%) for hours 2–24 of release day to `/output`.

**Method.** Each case carries ~40 past big game launches with their full hourly curves. The program rebuilds every comparable's release-day log shape relative to its own hour 1, takes the per-hour median shape — a dip through the UTC morning, a climb into the UTC-evening peak — shrinks it toward the persistence baseline, and centres a baseline-style widening log-normal spread on it. The calibration constants were picked by leave-one-out backtest over the comparables (see `backtest.py`): on the rolling-midnight console launches that resemble this bounty the template scores ≈0.22 mean pinball loss vs the house baseline's ≈0.27 on the same launches. Similarity kernels and per-hour tuning scored worse out of sample and were rejected.

## Run it

```sh
mkdir -p out
MAKEFUN_INPUT_DIR=<dir with .in cases> MAKEFUN_OUTPUT_DIR=out python3 main.py
python3 backtest.py <kit input dir>   # leave-one-out scores vs baseline
```

---
<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
