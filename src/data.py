"""Raw OHLCV ingestion. Network I/O only — no bar logic, no features.

The data window is pinned (SINCE/UNTIL) so a fresh clone reproduces the exact
dataset behind every figure in this repo. Everything after UNTIL is left
untouched as a true out-of-sample holdout.
"""
from pathlib import Path

import ccxt
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

SYMBOL, TIMEFRAME, EXCHANGE = "BTC/USDT", "1m", "binance"
SINCE = "2026-02-01T00:00:00Z"
UNTIL = "2026-08-01T00:00:00Z"

COLUMNS = ["ts", "open", "high", "low", "close", "volume"]


def fetch_ohlcv(symbol=SYMBOL, timeframe=TIMEFRAME, since=SINCE, until=UNTIL,
                exchange_id=EXCHANGE):
    """Page through the exchange REST API. Returns a UTC-indexed OHLCV frame."""
    exchange = getattr(ccxt, exchange_id)({"enableRateLimit": True})
    since_ms, until_ms = exchange.parse8601(since), exchange.parse8601(until)
    if until_ms <= since_ms:
        raise ValueError("until must be after since")

    limit, rows = 1000, []
    while True:
        batch = exchange.fetch_ohlcv(symbol, timeframe, since=since_ms, limit=limit)
        if not batch:
            break
        kept = [c for c in batch if c[0] < until_ms]
        rows += kept
        if rows:
            print(f"\r{len(rows):>9,} candles → "
                  f"{pd.to_datetime(rows[-1][0], unit='ms')}", end="", flush=True)
        if len(kept) < len(batch) or len(batch) < limit:
            break
        since_ms = batch[-1][0] + 1
    print()

    df = pd.DataFrame(rows, columns=COLUMNS)
    df["ts"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    return df.drop_duplicates("ts").set_index("ts").sort_index()


def cache_path(symbol=SYMBOL, timeframe=TIMEFRAME, since=SINCE, until=UNTIL):
    stem = f"{symbol.replace('/', '')}_{timeframe}_{since[:10]}_{until[:10]}"
    return DATA_DIR / f"{stem}.parquet"


def cached_ohlcv(symbol=SYMBOL, timeframe=TIMEFRAME, since=SINCE, until=UNTIL,
                 refresh=False):
    f = cache_path(symbol, timeframe, since, until)
    if f.exists() and not refresh:
        return pd.read_parquet(f)
    df = fetch_ohlcv(symbol, timeframe, since, until)
    df.to_parquet(f)
    return df


if __name__ == "__main__":
    df = cached_ohlcv()
    print(df.shape, df.index.min(), df.index.max())
