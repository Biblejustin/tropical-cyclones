"""Tropical cyclone analysis plots.

These plots describe a selected historical event list, not complete global
cyclone surveillance. Fatality totals combine physical hazard and human exposure.
Reference fits do not establish acceleration, flatness, or a power-law model.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

HERE = Path(__file__).parent
PLOTS = HERE / "plots"
PLOTS.mkdir(exist_ok=True)

CATALOG_START = 1850
CATALOG_END = 2024  # Explicit represented snapshot scope, not inferred surveillance coverage.
GREAT_CYCLONE_THRESHOLD = 10_000
PARTIAL_DECADE_START = 2020

plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 150, "savefig.bbox": "tight",
    "font.size": 10, "axes.titlesize": 12,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linestyle": "--",
})


def load_events() -> pd.DataFrame:
    df = pd.read_csv(HERE / "cyclones.csv")
    df["deaths_estimate"] = pd.to_numeric(df["deaths_estimate"], errors="coerce")
    return df


def fit_line(x, y, min_points=2):
    """Descriptive OLS with explicit guards for unusable or constant inputs."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    valid = np.isfinite(x) & np.isfinite(y)
    x, y = x[valid], y[valid]
    if len(x) < min_points or np.unique(x).size < 2:
        return None
    if np.ptp(y) == 0:
        return 0.0, float(y[0])
    centered = x - x.mean()
    variance = float(np.dot(centered, centered))
    if variance <= 0:
        return None
    slope = float(np.dot(centered, y-y.mean()) / variance)
    return slope, float(y.mean()-slope*x.mean())


def fmt_thousands(x, _):
    return f"{int(x):,}"


def plot_01_deaths_timeline(df: pd.DataFrame):
    df = df[df['deaths_estimate'] > 0].copy()
    fig, ax = plt.subplots(figsize=(11, 5.5))
    sizes = np.clip(np.sqrt(df["deaths_estimate"]) / 4, 30, 1200)
    colors = ["#cc3322" if d >= GREAT_CYCLONE_THRESHOLD else "#3377aa"
               for d in df["deaths_estimate"]]
    ax.scatter(df["year"], df["deaths_estimate"], s=sizes, c=colors, alpha=0.65,
                edgecolor="black", linewidth=0.5)
    ax.set_yscale("log")
    ax.set_ylabel("Deaths (log)")
    ax.set_xlabel("Year")
    ax.set_title("Selected cyclone deaths — red ≥10,000; bubble size ∝ √deaths")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_thousands))
    # Annotate biggest
    for _, row in df.nlargest(8, "deaths_estimate").iterrows():
        ax.annotate(row["name"].split(" (")[0][:18],
                    (row["year"], row["deaths_estimate"]),
                    xytext=(5, 5), textcoords="offset points", fontsize=8, alpha=0.85)
    plt.tight_layout()
    plt.savefig(PLOTS / "01_cyclone_deaths_timeline.png")
    plt.close()


def plot_02_decadal_counts_by_band(df: pd.DataFrame):
    df = df.copy()
    df["decade"] = (df["year"] // 10) * 10
    bands = [(1_000, 10_000, "1k–10k", "#aaccdd"),
             (10_000, 100_000, "10k–100k", "#dd9966"),
             (100_000, np.inf, "≥100k", "#cc3322")]
    fig, ax = plt.subplots(figsize=(11, 5))
    decades = np.arange(CATALOG_START, CATALOG_END+1, 10)
    bottom = np.zeros(len(decades))
    for lo, hi, label, color in bands:
        counts = []
        for d in decades:
            n = ((df["decade"] == d) &
                 (df["deaths_estimate"] >= lo) &
                 (df["deaths_estimate"] < hi)).sum()
            counts.append(n)
        ax.bar(decades, counts, width=8, bottom=bottom, label=label,
                color=color, edgecolor="black", linewidth=0.4)
        bottom += counts
    ax.axvspan(PARTIAL_DECADE_START, PARTIAL_DECADE_START + 10,
                color="grey", alpha=0.18, label="partial decade in snapshot")
    # Multi-era trend lines
    totals = np.array(bottom, dtype=float)
    eras = [
        (CATALOG_START, "Selected decades 1850+", "#222222", "--"),
        (1944, "Selected decades 1950+", "#33aa66", ":"),
        (1979, "Selected decades 1980+", "#3366cc", "-."),
    ]
    fits = []
    rng = np.random.default_rng(42)
    for era_start, label, color, ls in eras:
        mask = (decades >= era_start) & (decades < PARTIAL_DECADE_START)
        if mask.sum() < 3:
            fits.append((label, np.nan, np.nan, np.nan)); continue
        x_fit = decades[mask].astype(float); y_fit = totals[mask]
        fit = fit_line(x_fit, y_fit, min_points=3)
        if fit is None:
            fits.append((label, np.nan, np.nan, np.nan)); continue
        slope, intercept = fit
        boots = []
        for _ in range(2000):
            idx = rng.integers(0, len(x_fit), len(x_fit))
            # A bootstrap draw may repeat one decade exclusively; its slope
            # is undefined and must not enter the resampling distribution.
            if np.unique(x_fit[idx]).size < 2:
                continue
            draw = fit_line(x_fit[idx], y_fit[idx])
            if draw is not None:
                boots.append(draw[0])
        lo, hi = np.percentile(boots, [2.5, 97.5]) if len(boots) >= 2 else (np.nan, np.nan)
        line_x = np.linspace(x_fit.min(), x_fit.max(), 50)
        ax.plot(line_x, slope * line_x + intercept, ls, color=color,
                  linewidth=1.6,
                  label=f"{label}: Δ count/decade {slope*10:+.2f} [bootstrap {lo*10:+.2f}, {hi*10:+.2f}]")
        fits.append((label, slope, lo, hi))
    ax.set_xlabel("Decade")
    ax.set_ylabel("Listed cyclones per decade")
    ax.set_title(f"Selected cyclone counts by death band ({CATALOG_START}–{CATALOG_END}); descriptive fits")
    ax.legend(loc="upper left", fontsize=8)
    plt.tight_layout()
    plt.savefig(PLOTS / "02_decadal_counts_by_band.png")
    plt.close()
    return fits


def plot_03_great_cyclone_timing(df: pd.DataFrame):
    great = df[(df["deaths_estimate"] >= GREAT_CYCLONE_THRESHOLD) &
               df['year'].between(CATALOG_START, CATALOG_END)].sort_values("year").reset_index(drop=True)
    great["n"] = np.arange(1, len(great) + 1)
    if len(great) < 2:
        return
    span_yr = CATALOG_END - CATALOG_START + 1
    if span_yr <= 0:
        return
    rate = len(great) / span_yr

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    yrs = np.arange(CATALOG_START, CATALOG_END+2)
    ax = axes[0]
    ax.step(np.r_[great["year"], CATALOG_END+1], np.r_[great["n"], len(great)], where="post",
            color="#cc3322", linewidth=2, label="Listed ≥10k cumulative")
    ax.plot(yrs, rate * (yrs - CATALOG_START), color="gray", linestyle="--",
            label=f"Selected-list reference ({rate:.3f}/yr)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative listed ≥10,000-death cyclones")
    ax.set_title(f"Selected events vs fixed-scope reference ({CATALOG_START}–{CATALOG_END})")
    ax.legend()

    ax = axes[1]
    intervals = np.diff(great["year"].values)
    if len(intervals) > 0:
        ax.bar(range(len(intervals)), intervals,
                color="#cc3322", alpha=0.7, edgecolor="black", linewidth=0.4)
        ax.axhline(intervals.mean(), color="gray", linestyle="--",
                    label=f"mean = {intervals.mean():.1f} yr")
        ax.set_xticks(range(len(intervals)))
        ax.set_xticklabels([f"#{i+1}" for i in range(len(intervals))], fontsize=8)
        ax.set_ylabel("Years between listed onsets")
        ax.set_title("Year-resolution gaps within selected list")
        ax.legend()
    plt.tight_layout()
    plt.savefig(PLOTS / "03_great_cyclone_timing.png")
    plt.close()


def plot_04_magnitude_distribution(df: pd.DataFrame):
    deaths = df["deaths_estimate"].values
    deaths = deaths[deaths > 0]
    deaths = np.sort(deaths)[::-1]
    survival = np.arange(1, len(deaths) + 1)

    tail_mask = deaths >= 1000
    if tail_mask.sum() >= 5:
        x_tail = np.log10(deaths[tail_mask])
        y_tail = np.log10(survival[tail_mask])
        fit = fit_line(x_tail, y_tail, min_points=5)
        if fit is not None:
            slope, intercept = fit
            alpha = -slope
        else:
            alpha = None
    else:
        alpha = None

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.loglog(deaths, survival, "o", color="#cc3322", alpha=0.7,
                markeredgecolor="black", markersize=6, label="Listed cyclones")
    if alpha is not None:
        xs = np.logspace(np.log10(1000), np.log10(deaths.max()), 50)
        ys = 10 ** intercept * xs ** slope
        ax.loglog(xs, ys, "--", color="gray", label=f"Descriptive log-log slope −{alpha:.2f}")
    ax.set_xlabel("Deaths (log)")
    ax.set_ylabel("Survival count")
    ax.set_title("Selected death-toll distribution (≥1,000-death reference line)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(PLOTS / "04_death_distribution.png")
    plt.close()


def main():
    df = load_events()
    print(f"Loaded {len(df)} cyclones; {int(df['year'].min())}–{int(df['year'].max())}")
    print(f"≥10,000 deaths: {(df['deaths_estimate'] >= GREAT_CYCLONE_THRESHOLD).sum()}")
    plot_01_deaths_timeline(df)
    fits = plot_02_decadal_counts_by_band(df)
    for label, slope, lo, hi in fits:
        print(f"  {label:<40} Δ count/decade {slope*10:+.2f} [bootstrap range {lo*10:+.2f}, {hi*10:+.2f}]")
    plot_03_great_cyclone_timing(df)
    plot_04_magnitude_distribution(df)
    print("Fits describe selected catalogue rows; completeness and population trends are unestablished.")
    print(f"Wrote 4 plots to {PLOTS}/")


if __name__ == "__main__":
    main()
