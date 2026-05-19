# tropical-cyclones

Major hurricanes / typhoons / cyclones with ≥1000 deaths (with a few notable lower-death events included for impact).

Parallel to `earthquakes`, `spaceweather`, `famines-tracking`, `flood-data`, `pandemics-tracking`, `volcanic-eruptions`.

## Quick findings

- **37 major cyclones since 1737**; **18 with ≥10,000 deaths**.
- **Bay of Bengal dominates the top of the distribution**: 1737 Hooghly River cyclone (300k), 1970 Bhola (500k — deadliest tropical cyclone ever recorded), 1881 Haiphong (300k), 1839 Coringa (300k), 1876 Backergunge (200k), 1991 Bangladesh cyclone (138k).
- **No deadly-event drop-off in modern era despite forecasting improvements** — recent events like 2008 Cyclone Nargis (138k, Myanmar) and 2013 Typhoon Haiyan (6,340, Philippines) show that political/preparedness factors still drive death tolls more than meteorology.
- **Post-1850 decadal trend = +0.017 cyclones/decade [95% CI +0.004, +0.026]** — small positive, but this is mostly catalog cleanup of pre-1900 undercounting. The 1950+ trend is flat.
- **Power-law tail with α ≈ 0.43** on the log-log survival curve above 1,000 deaths. Same regime as quakes/famines/wars but flatter (heavier tail) — death tolls concentrate at the extreme.
- **No US event over 10,000 deaths since 1900 Galveston** (≈8,000). Modern US cyclone deaths are dominated by inland flooding and infrastructure failure (Katrina 2005, Maria 2017, Helene 2024), not direct storm winds.

## Sample output

### Cyclone deaths over time

Deaths vs year, log scale; red = ≥10,000 deaths. The biggest events are annotated. Notable: the Bay of Bengal dominates the top of the distribution, and the 21st century is conspicuously full of mid-tier events but light on ≥100k catastrophes.

**In plain English:** Each circle is one cyclone. The higher it is, the deadlier; the redder it is, the more catastrophic. The y-axis is log scale, meaning each step up is 10× more deaths — needed because death tolls range from hundreds to half a million. Most of the very-deadliest cyclones happened in the Bay of Bengal (Bhola 1970, Hooghly 1737, Haiphong 1881) — that region's combination of shallow water, dense coastal population, and storm tracks makes it the deadliest cyclone basin on Earth.

![Cyclone deaths timeline](plots/01_cyclone_deaths_timeline.png)

### Cyclones per decade by death band

Stacked bars: cyclones per decade by death band (1k–10k, 10k–100k, ≥100k), 1850+. Dashed OLS trend with bootstrap 95% CI. The visible upward slope is mostly a pre-1900 detection-floor artifact; post-1900 the rate is roughly steady.

**In plain English:** Each bar shows how many deadly cyclones occurred in that 10-year period. The dashed line is the trend — slightly upward, but most of that slope reflects records being more complete after 1900, not actual storms getting more frequent. Inside the modern era (post-1950 with aircraft reconnaissance and satellites), the count is roughly steady.

![Decadal counts](plots/02_decadal_counts_by_band.png)

### Great cyclone timing (≥10,000 deaths)

Cumulative ≥10,000-death cyclone count since 1850 vs the constant-rate reference. Tests whether catastrophic cyclones are accelerating or steady-state.

**In plain English:** Same idea as the volcano and pandemic versions. The grey line is "what we'd see if catastrophic cyclones came at a steady pace." The red staircase is what actually happened. When the staircase tracks the line, the rate is steady; when it pulls ahead or behind, that's a busy or quiet stretch.

![Great cyclone timing](plots/03_great_cyclone_timing.png)

### Death-toll distribution

Log-log survival function with power-law fit on the ≥1,000-death tail. α ≈ 0.43 — the heaviest tail of any disaster category in this project. A single Bhola-class event dominates the very-large-deaths bin.

**In plain English:** Reading the dots right to left: the further right, the deadlier; the lower a dot, the rarer events at that level are. The dashed line shows the predictable pattern that connects "small common cyclones" to "rare huge ones." The slope (α ≈ 0.43) is shallow compared to most other disaster categories — meaning when cyclones go bad, they go really bad. A single Bhola 1970 (500,000 deaths) is in a category of its own.

![Death distribution](plots/04_death_distribution.png)

## What's in it

`cyclones.csv` — columns:

- `year`, `month` — landfall / peak
- `name` — common name (modern events have official IBTrACS names; pre-1953 unnamed events listed by location)
- `region`
- `deaths_estimate`
- `sources_notes`

Coverage: 1737 Hooghly River cyclone → 2024 Helene/Milton.

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
