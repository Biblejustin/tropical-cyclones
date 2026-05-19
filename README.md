# tropical-cyclones

Major hurricanes / typhoons / cyclones with ≥1000 deaths (with a few notable lower-death events included for impact).

Parallel to `earthquakes`, `spaceweather`, `famines-tracking`, `flood-data`, `pandemics-tracking`, `volcanic-eruptions`.

## Quick findings

- **37 major cyclones since 1737**; **18 with ≥10,000 deaths**.
- **Bay of Bengal dominates the top of the distribution**: 1737 Hooghly River cyclone (300k), 1970 Bhola (500k — deadliest tropical cyclone ever recorded), 1881 Haiphong (300k), 1839 Coringa (300k), 1876 Backergunge (200k), 1991 Bangladesh cyclone (138k).
- **No deadly-event drop-off in modern era despite forecasting improvements** — recent events like 2008 Cyclone Nargis (138k, Myanmar) and 2013 Typhoon Haiyan (6,340, Philippines) show that political/preparedness factors still drive death tolls more than meteorology.
- **Power-law tail with α ≈ 0.43** on the log-log survival curve above 1,000 deaths. Same regime as quakes/famines/wars but flatter (heavier tail) — death tolls concentrate at the extreme.
- **No US event over 10,000 deaths since 1900 Galveston** (≈8,000). Modern US cyclone deaths are dominated by inland flooding and infrastructure failure (Katrina 2005, Maria 2017, Helene 2024), not direct storm winds.

See `plots/` for the four charts.

## What's in it

`cyclones.csv` — columns:

- `year`, `month` — landfall / peak
- `name` — common name (modern events have official IBTrACS names; pre-1953 unnamed events listed by location)
- `region`
- `deaths_estimate`
- `sources_notes`

Coverage: 1737 Hooghly River cyclone → 2024 Helene/Milton.

## Plots

`make_plots.py` generates four standalone analytical plots:

### `plots/01_cyclone_deaths_timeline.png`
Deaths vs year scatter, log y-axis, red = ≥10,000 deaths. Bubble size ∝ √deaths. Annotated outliers include Bhola, Hooghly, Haiphong, Coringa.

### `plots/02_decadal_counts_by_band.png`
Stacked bars: cyclones per decade by death band (1k–10k, 10k–100k, ≥100k). Catalog starts 1850 for trend purposes.

### `plots/03_great_cyclone_timing.png`
Cumulative ≥10,000-death cyclone count vs constant-rate reference + inter-event interval bar chart. Tests whether catastrophic cyclones are accelerating or steady-state.

### `plots/04_death_distribution.png`
Log-log survival function with power-law fit on the ≥1,000-death tail. α ≈ 0.43 (heavy tail).

## Detection-bias notes

| Era | Coverage |
|---|---|
| Pre-1850 | Concentrated on European-colonial-trade-routes events; non-impacting cyclones unrecorded |
| 1850–1900 | Telegraph-era; coastal landfalls in inhabited regions documented |
| 1900–1950 | Meteorological services in major basins; open-ocean cyclones still missed |
| 1950–present | Aircraft reconnaissance + radar; near-complete for Cat 1+ landfalls |
| 1979–present | Satellite era; complete for tropical-storm-strength systems globally (IBTrACS) |

For correlation work, **≥1000-deaths is the detection-clean band back to ~1850** (and arguably earlier in the Bay of Bengal, which has been a population hotspot for cyclone-prone shoreline for millennia).

## Reproducing the plots

```bash
python3 -m venv .venv
.venv/bin/pip install pandas numpy matplotlib
.venv/bin/python make_plots.py
```

## Source

- Primary: IBTrACS (International Best Track Archive for Climate Stewardship), NOAA — https://www.ncei.noaa.gov/products/international-best-track-archive
- Pre-IBTrACS events: Boose et al. (2004), Emanuel (2005), various national meteorological records
- Death-toll consensus from EM-DAT and the Centre for Research on the Epidemiology of Disasters

## Intended use

Data source for tropical-cyclone correlation tests in [`Biblejustin/correlations`](https://github.com/Biblejustin/correlations).
