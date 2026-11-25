"""
CCP Margin & Default Fund Stress Test
=====================================
A simplified model of how a central counterparty (CCP) such as NSE Clearing
protects itself against clearing-member defaults in NIFTY index futures.

Steps
1. Load daily NIFTY 50 closing prices.
2. Give 10 hypothetical clearing members long/short NIFTY futures positions.
3. Initial margin (IM): 99% historical VaR over a 2-day margin period of risk,
   plus an extreme loss margin (ELM).
4. Back-test the margin model: how often did a 2-day move beat the IM rate?
5. Stress scenarios: worst historical 2-day moves + hypothetical shocks.
6. Uncovered loss per member = stress loss - margin held.
7. Cover 1 / Cover 2 / Cover 3: can the default fund absorb the default of
   the 1, 2 or 3 members with the largest uncovered losses?
8. Default waterfall: which layer absorbs the worst-case Cover 2 loss.

Data
- Put a CSV at data/nifty.csv with columns Date, Close (export from NSE or
  Yahoo Finance, ticker ^NSEI), OR install yfinance and the script downloads it.
- If neither is available the script falls back to SIMULATED prices so the
  code still runs. Results from simulated data are for testing only.

All money figures are in INR crore. Member positions, the default fund size
and the margin parameters are assumptions, not NSE Clearing's real figures.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "data" / "nifty.csv"
OUT = HERE / "output"
OUT.mkdir(exist_ok=True)

# ----------------------------------------------------------------------------
# Assumptions (change these to test different set-ups)
# ----------------------------------------------------------------------------
START_DATE = "2010-01-01"
VAR_CONFIDENCE = 0.99        # IM covers 99% of 2-day moves
MPOR_DAYS = 2                # margin period of risk (days to close out a defaulter)
ELM_RATE = 0.02              # extreme loss margin, % of notional (assumption)
DEFAULT_FUND = 1_500.0       # Core SGF-style default fund for this book, INR crore
CC_SKIN_IN_GAME_PCT = 0.05   # CCP's own capital ahead of the fund: 5% of the fund
HYPOTHETICAL_SHOCKS = {"Hypothetical -10%": -0.10,
                       "Hypothetical -15%": -0.15,
                       "Hypothetical +12%": 0.12}

# Net NIFTY futures notional per member, INR crore (+ long, - short)
MEMBERS = pd.Series({
    "CM01 Bank broker":       4_200,
    "CM02 Foreign bank":     -3_800,
    "CM03 Retail broker A":   2_900,
    "CM04 Prop trader":      -5_100,
    "CM05 Retail broker B":   1_600,
    "CM06 Custodian (FPI)":   6_000,
    "CM07 Discount broker":  -2_200,
    "CM08 Arbitrage desk":     -900,
    "CM09 Regional broker":    1_100,
    "CM10 Market maker":     -4_400,
}, name="notional_cr")


# ----------------------------------------------------------------------------
# 1. Data
# ----------------------------------------------------------------------------
def load_prices() -> tuple[pd.Series, str]:
    """Return NIFTY closes and a label saying where they came from."""
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE, parse_dates=["Date"], dayfirst=True)
        s = df.set_index("Date")["Close"].sort_index().astype(float)
        return s[s.index >= START_DATE], f"real data from {DATA_FILE.name}"
    try:
        import yfinance as yf
        df = yf.download("^NSEI", start=START_DATE, progress=False, auto_adjust=True)
        s = df["Close"].squeeze().dropna()
        if len(s) > 500:
            DATA_FILE.parent.mkdir(exist_ok=True)
            s.rename("Close").to_frame().to_csv(DATA_FILE, index_label="Date")
            return s, "real data from Yahoo Finance (^NSEI)"
    except Exception:
        pass
    return simulate_prices(), "SIMULATED data (testing only, not real NIFTY)"


def simulate_prices(n_days: int = 4_000, seed: int = 7) -> pd.Series:
    """Fat-tailed random walk with two crash periods, used only as a fallback."""
    rng = np.random.default_rng(seed)
    t_draws = rng.standard_t(df=4, size=n_days) / np.sqrt(2)   # unit variance
    vol = np.full(n_days, 0.011)
    vol[1_200:1_260] = 0.022      # crisis 1
    vol[2_600:2_640] = 0.028      # crisis 2
    rets = 0.0004 + vol * t_draws
    rets[2_610] = -0.12           # one crash day
    idx = pd.bdate_range(START_DATE, periods=n_days)
    return pd.Series(5_000 * np.exp(np.cumsum(rets)), index=idx, name="Close")


# ----------------------------------------------------------------------------
# 2-3. Margin
# ----------------------------------------------------------------------------
def margin_rates(prices: pd.Series) -> dict:
    """Historical-VaR IM rate on overlapping MPOR-day returns."""
    r_mpor = prices.pct_change(MPOR_DAYS).dropna()
    var_long = -np.quantile(r_mpor, 1 - VAR_CONFIDENCE)   # loss for a long
    var_short = np.quantile(r_mpor, VAR_CONFIDENCE)       # loss for a short
    return {"im_long": var_long, "im_short": var_short,
            "im_rate": max(var_long, var_short), "returns": r_mpor}


def member_margins(rates: dict) -> pd.DataFrame:
    df = MEMBERS.to_frame()
    df["side"] = np.where(df.notional_cr > 0, "Long", "Short")
    df["im_cr"] = df.notional_cr.abs() * rates["im_rate"]
    df["elm_cr"] = df.notional_cr.abs() * ELM_RATE
    df["margin_cr"] = df.im_cr + df.elm_cr
    return df


# ----------------------------------------------------------------------------
# 4. Back-test
# ----------------------------------------------------------------------------
def backtest(prices: pd.Series, window: int = 750) -> pd.DataFrame:
    """
    Rolling test: each day set the IM rate from the previous `window` days,
    then check whether the next MPOR-day move (either direction) beat it.
    """
    r = prices.pct_change(MPOR_DAYS)
    rows = []
    for i in range(window, len(prices) - MPOR_DAYS):
        hist = r.iloc[i - window + MPOR_DAYS:i].dropna()
        im = max(-np.quantile(hist, 1 - VAR_CONFIDENCE),
                 np.quantile(hist, VAR_CONFIDENCE))
        move = prices.iloc[i + MPOR_DAYS] / prices.iloc[i] - 1
        rows.append((prices.index[i], im, move, abs(move) > im))
    return pd.DataFrame(rows, columns=["date", "im_rate", "move", "breach"])


# ----------------------------------------------------------------------------
# 5-7. Stress tests
# ----------------------------------------------------------------------------
def build_scenarios(rates: dict, simulated: bool = False) -> pd.Series:
    r = rates["returns"]
    worst_down, worst_up = r.idxmin(), r.idxmax()
    if simulated:   # simulated dates mean nothing, so leave them out
        sc = {"Worst sim. 2-day fall": r.min(), "Worst sim. 2-day rise": r.max()}
    else:
        sc = {f"Worst hist. 2-day fall ({worst_down:%d %b %Y})": r.min(),
              f"Worst hist. 2-day rise ({worst_up:%d %b %Y})": r.max()}
    sc.update(HYPOTHETICAL_SHOCKS)
    return pd.Series(sc, name="move")


def stress_losses(margins: pd.DataFrame, scenarios: pd.Series) -> pd.DataFrame:
    """Uncovered loss (INR crore) for every member under every scenario."""
    out = {}
    for name, move in scenarios.items():
        loss = (-margins.notional_cr * move).clip(lower=0)
        out[name] = (loss - margins.margin_cr).clip(lower=0)
    return pd.DataFrame(out)


def cover_test(uncovered: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sc in uncovered.columns:
        top = uncovered[sc].sort_values(ascending=False)
        rows.append({"scenario": sc,
                     "cover_1": top.iloc[:1].sum(),
                     "cover_2": top.iloc[:2].sum(),
                     "cover_3": top.iloc[:3].sum(),
                     "defaulters_cover_2": ", ".join(top.index[:2].str[:4])})
    df = pd.DataFrame(rows).set_index("scenario")
    resources = DEFAULT_FUND * (1 + CC_SKIN_IN_GAME_PCT)
    for c in ["cover_1", "cover_2", "cover_3"]:
        df[c + "_ok"] = df[c] <= resources
    return df


# ----------------------------------------------------------------------------
# 8. Default waterfall (SEBI-style order, simplified)
# ----------------------------------------------------------------------------
def waterfall(loss: float) -> pd.DataFrame:
    """
    Margins of the defaulters are already used up (loss is net of them).
    Remaining layers, in order:
      1. CCP skin in the game (5% of the fund)
      2. Default fund (Core SGF)
      3. Remaining CCP resources (assumed 1x the fund)
      4. Capped assessment on surviving members (assumed 20% of the fund)
      5. Haircut on payouts (whatever is left)
    """
    layers = [("CCP skin in the game", DEFAULT_FUND * CC_SKIN_IN_GAME_PCT),
              ("Default fund (Core SGF)", DEFAULT_FUND),
              ("Remaining CCP resources", DEFAULT_FUND * 1.0),
              ("Member assessment (capped)", DEFAULT_FUND * 0.20),
              ("Payout haircut", np.inf)]
    left, rows = loss, []
    for name, size in layers:
        used = min(left, size)
        rows.append({"layer": name, "size_cr": size, "used_cr": used})
        left -= used
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# Charts
# ----------------------------------------------------------------------------
BLUE, RED, GREY, GREEN = "#2f5d8a", "#c0504d", "#9aa5b1", "#4f8a5b"


def plot_backtest(bt: pd.DataFrame, path: Path):
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(bt.date, bt.move * 100, color=GREY, lw=0.6, label="2-day NIFTY move")
    ax.plot(bt.date, bt.im_rate * 100, color=BLUE, lw=1.2, label="IM rate (+)")
    ax.plot(bt.date, -bt.im_rate * 100, color=BLUE, lw=1.2, label="IM rate (-)")
    b = bt[bt.breach]
    ax.scatter(b.date, b.move * 100, color=RED, s=12, zorder=3, label="Breach")
    ax.set_ylabel("%")
    ax.set_title("Margin back-test: 2-day moves vs 99% VaR margin rate")
    ax.legend(loc="lower left", fontsize=8, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_cover(cov: pd.DataFrame, path: Path):
    fig, ax = plt.subplots(figsize=(9, 4))
    x = np.arange(len(cov))
    w = 0.27
    for i, (c, col) in enumerate([("cover_1", GREY), ("cover_2", BLUE), ("cover_3", RED)]):
        ax.bar(x + (i - 1) * w, cov[c], w, color=col, label=c.replace("_", " ").title())
    ax.axhline(DEFAULT_FUND * (1 + CC_SKIN_IN_GAME_PCT), color="black", ls="--", lw=1,
               label="Default fund + skin in the game")
    ax.set_xticks(x, [s.replace(" (", "\n(") for s in cov.index], fontsize=7)
    ax.set_ylabel("Uncovered loss, INR crore")
    ax.set_title("Cover 1 / 2 / 3 stress losses vs default resources")
    ax.legend(fontsize=8, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_waterfall(wf: pd.DataFrame, loss: float, title: str, path: Path):
    used = wf[wf.used_cr > 0]
    fig, ax = plt.subplots(figsize=(8, 3.8))
    bottom = 0.0
    for _, row in used.iterrows():
        colour = RED if row.layer in ("Member assessment (capped)", "Payout haircut") else BLUE
        ax.bar(row.layer, row.used_cr, bottom=bottom, color=colour)
        small = row.used_cr < 0.08 * loss
        ax.text(row.layer, bottom + (row.used_cr + loss * 0.02 if small else row.used_cr / 2),
                f"{row.used_cr:,.0f}", ha="center", va="bottom" if small else "center",
                color="black" if small else "white", fontsize=9)
        bottom += row.used_cr
    ax.set_ylabel("INR crore")
    ax.set_title(f"Default waterfall for the worst Cover 2 loss ({loss:,.0f} cr)\n{title}",
                 fontsize=10)
    ax.tick_params(axis="x", labelsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ----------------------------------------------------------------------------
def main():
    prices, source = load_prices()
    print(f"Data: {source} | {prices.index[0]:%d %b %Y} to {prices.index[-1]:%d %b %Y}"
          f" | {len(prices):,} days\n")

    rates = margin_rates(prices)
    print(f"IM rate (99% VaR, {MPOR_DAYS}-day): long {rates['im_long']:.2%}, "
          f"short {rates['im_short']:.2%} -> using {rates['im_rate']:.2%} + ELM {ELM_RATE:.0%}\n")

    margins = member_margins(rates)
    print("Member margins (INR crore)")
    print(margins.round(1).to_string(), "\n")

    bt = backtest(prices)
    n, k = len(bt), int(bt.breach.sum())
    print(f"Back-test: {k} breaches in {n:,} days = {k / n:.2%} "
          f"(a 99% model should breach about {1 - VAR_CONFIDENCE:.0%} on each side,"
          f" ~{2 * (1 - VAR_CONFIDENCE):.0%} in total)\n")

    scenarios = build_scenarios(rates, simulated=source.startswith("SIMULATED"))
    uncovered = stress_losses(margins, scenarios)
    cover = cover_test(uncovered)
    print("Scenarios:", ", ".join(f"{k}: {v:+.1%}" for k, v in scenarios.items()), "\n")
    print("Uncovered losses by member (INR crore)")
    print(uncovered.round(0).to_string(), "\n")
    print(f"Cover test vs resources of {DEFAULT_FUND * (1 + CC_SKIN_IN_GAME_PCT):,.0f} cr")
    print(cover.round(0).to_string(), "\n")

    worst_sc = cover.cover_2.idxmax()
    worst_loss = cover.loc[worst_sc, "cover_2"]
    wf = waterfall(worst_loss)
    print(f"Waterfall for worst Cover 2 loss ({worst_sc}):")
    print(wf.replace(np.inf, np.nan).round(0).to_string(index=False), "\n")

    # Default fund size a Cover 2 standard would need (the MRC idea)
    print(f"Fund needed for Cover 2 across these scenarios: {cover.cover_2.max():,.0f} cr"
          f" | Cover 3: {cover.cover_3.max():,.0f} cr | Fund held: {DEFAULT_FUND:,.0f} cr")

    margins.round(2).to_csv(OUT / "member_margins.csv")
    uncovered.round(2).to_csv(OUT / "uncovered_losses.csv")
    cover.round(2).to_csv(OUT / "cover_test.csv")
    wf.replace(np.inf, np.nan).round(2).to_csv(OUT / "waterfall.csv", index=False)
    plot_backtest(bt, OUT / "backtest.png")
    plot_cover(cover, OUT / "cover_test.png")
    plot_waterfall(wf, worst_loss, worst_sc, OUT / "waterfall.png")
    (OUT / "data_source.txt").write_text(source + "\n")
    print(f"\nCharts and tables saved to {OUT}")


if __name__ == "__main__":
    main()
