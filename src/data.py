"""Raw OHLCV ingestion. Network I/O only — no bar logic, no features."""
from pathlib import Path
import ccxt
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def fetch_ohlcv(symbol="BTC/USDT", timeframe="1m",
                since="2026-02-01T00:00:00Z", exchange_id="binance"):
    exchange = getattr(ccxt, exchange_id)({"enableRateLimit": True})
    since_ms, limit, rows = exchange.parse8601(since), 1000, []
    while True:
        batch = exchange.fetch_ohlcv(symbol, timeframe, since=since_ms, limit=limit)
        if not batch:
            break
        rows += batch
        since_ms = batch[-1][0] + 1
        print(f"\r{len(rows):,} candles → "
              f"{pd.to_datetime(batch[-1][0], unit='ms')}", end="")
        if len(batch) < limit:
            break
    df = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close", "volume"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    return df.drop_duplicates("ts").set_index("ts").sort_index()


def cached_ohlcv(symbol="BTC/USDT", timeframe="1m",
                 since="2026-02-01T00:00:00Z", refresh=False):
    f = DATA_DIR / f"{symbol.replace('/', '')}_{timeframe}_{since[:10]}.parquet"
    if f.exists() and not refresh:
        return pd.read_parquet(f)
    df = fetch_ohlcv(symbol, timeframe, since)
    df.to_parquet(f)
    return df


if __name__ == "__main__":
    df = cached_ohlcv()
    print(df.shape, df.index.min(), df.index.max())
