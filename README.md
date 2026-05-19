# tropical-cyclones

Major hurricanes / typhoons / cyclones with ≥1000 deaths (with a few notable lower-death events included for impact).

Parallel to `earthquakes`, `spaceweather`, `famines-tracking`, `flood-data`, `pandemics-tracking`, `volcanic-eruptions`.

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

## Source

- Primary: IBTrACS (International Best Track Archive for Climate Stewardship), NOAA — https://www.ncei.noaa.gov/products/international-best-track-archive
- Pre-IBTrACS events: Boose et al. (2004), Emanuel (2005), various national meteorological records
- Death-toll consensus from EM-DAT and the Centre for Research on the Epidemiology of Disasters

## Intended use

Data source for tropical-cyclone correlation tests in [`Biblejustin/correlations`](https://github.com/Biblejustin/correlations).
