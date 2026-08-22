import pandas as pd
from src.data import cached_ohlcv, SINCE, UNTIL

df = cached_ohlcv()
expected = pd.date_range(df.index.min(), df.index.max(), freq="1min")
missing = expected.difference(df.index)

print("window          :", SINCE, "→", UNTIL)
print("rows            :", f"{len(df):,}")
print("expected minutes:", f"{len(expected):,}")
print("missing minutes :", f"{len(missing):,} ({len(missing)/len(expected):.4%})")
print("duplicate ts    :", df.index.duplicated().sum())
print("monotonic       :", df.index.is_monotonic_increasing)
print("zero-volume     :", (df.volume == 0).sum())
print("non-positive px :", (df[['open','high','low','close']] <= 0).sum().sum())
