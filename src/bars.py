def time_bars(df, freq="1h"):
    """Clock-time OHLCV bars. The baseline every dollar-bar claim is measured against."""
    # resample(freq).agg(...) → open: first, high: max, low: min,
    # close: last, volume: sum; then drop empty periods
