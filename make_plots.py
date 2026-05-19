"""Tropical cyclone analysis plots.

Conventions:
- Detection-clean for ≥1000 deaths since ~1850 (telegraph era)
- Aircraft recon 1944+; satellite 1979+
- Cumulative-vs-constant for ≥10,000-death cyclones
- Power-law on the tail
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
    df["deaths_estimate"] = pd.to_numeric(df["deaths_estimate"], errors="coerce").fillna(0)
    return df


def fmt_thousands(x, _):
    return f"{int(x):,}"


def plot_01_deaths_timeline(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 5.5))
    sizes = np.clip(np.sqrt(df["deaths_estimate"]) / 4, 30, 1200)
    colors = ["#cc3322" if d >= GREAT_CYCLONE_THRESHOLD else "#3377aa"
               for d in df["deaths_estimate"]]
    ax.scatter(df["year"], df["deaths_estimate"], s=sizes, c=colors, alpha=0.65,
                edgecolor="black", linewidth=0.5)
    ax.set_yscale("log")
    ax.set_ylabel("Deaths (log)")
    ax.set_xlabel("Year")
    ax.set_title("Tropical cyclone deaths over time — red = ≥10,000 deaths, bubble size ∝ √deaths")
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
    decades = np.arange(CATALOG_START, 2030, 10)
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
                color="grey", alpha=0.18, label="partial")
    totals = np.array(bottom)
    full_mask = decades < PARTIAL_DECADE_START
    x_fit = decades[full_mask]; y_fit = totals[full_mask]
    slope, intercept = np.polyfit(x_fit, y_fit, 1)
    rng = np.random.default_rng(42)
    boot = []
    for _ in range(2000):
        idx = rng.integers(0, len(x_fit), len(x_fit))
        s, _ = np.polyfit(x_fit[idx], y_fit[idx], 1)
        boot.append(s)
    ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
    ax.plot(decades, slope * decades + intercept, "k--", linewidth=1.5,
              label=f"OLS trend: {slope:+.3f}/decade  [95% CI {ci_lo:+.3f}, {ci_hi:+.3f}]")
    ax.set_xlabel("Decade")
    ax.set_ylabel("Cyclones per decade")
    ax.set_title(f"Cyclones per decade by death band (catalog ≥{CATALOG_START})")
    ax.legend(loc="upper left", fontsize=9)
    plt.tight_layout()
    plt.savefig(PLOTS / "02_decadal_counts_by_band.png")
    plt.close()
    return slope, ci_lo, ci_hi


def plot_03_great_cyclone_timing(df: pd.DataFrame):
    great = df[df["deaths_estimate"] >= GREAT_CYCLONE_THRESHOLD].sort_values("year").reset_index(drop=True)
    great["n"] = np.arange(1, len(great) + 1)
    if len(great) < 2:
        return
    span_yr = great["year"].iloc[-1] - CATALOG_START
    rate = len(great) / span_yr

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    yrs = np.arange(CATALOG_START, 2026)
    ax = axes[0]
    ax.step(great["year"], great["n"], where="post",
            color="#cc3322", linewidth=2, label="Observed ≥10k cumulative")
    ax.plot(yrs, rate * (yrs - CATALOG_START), color="gray", linestyle="--",
            label=f"Constant rate ({rate:.3f}/yr)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative ≥10,000-death cyclones")
    ax.set_title(f"Cumulative vs constant-rate ({CATALOG_START}+)")
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
        ax.set_ylabel("Years between great cyclones")
        ax.set_title("Inter-event intervals")
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
        slope, intercept = np.polyfit(x_tail, y_tail, 1)
        alpha = -slope
    else:
        alpha = None

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.loglog(deaths, survival, "o", color="#cc3322", alpha=0.7,
                markeredgecolor="black", markersize=6, label="Cyclones")
    if alpha is not None:
        xs = np.logspace(np.log10(1000), np.log10(deaths.max()), 50)
        ys = 10 ** intercept * xs ** slope
        ax.loglog(xs, ys, "--", color="gray", label=f"Power-law fit α={alpha:.2f}")
    ax.set_xlabel("Deaths (log)")
    ax.set_ylabel("Survival count")
    ax.set_title("Cyclone death-toll distribution (tail above 1,000)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(PLOTS / "04_death_distribution.png")
    plt.close()


def main():
    df = load_events()
    print(f"Loaded {len(df)} cyclones; {int(df['year'].min())}–{int(df['year'].max())}")
    print(f"≥10,000 deaths: {(df['deaths_estimate'] >= GREAT_CYCLONE_THRESHOLD).sum()}")
    plot_01_deaths_timeline(df)
    slope, lo, hi = plot_02_decadal_counts_by_band(df)
    print(f"Decadal trend ({CATALOG_START}+): {slope:+.3f}/decade [95% CI {lo:+.3f}, {hi:+.3f}]")
    plot_03_great_cyclone_timing(df)
    plot_04_magnitude_distribution(df)
    print(f"Wrote 4 plots to {PLOTS}/")


if __name__ == "__main__":
    main()
