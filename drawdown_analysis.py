#!/usr/bin/python3
"""
Drawdown Tracker

This script downloads historical price data for a given symbol and identifies
drawdowns relative to the all time peak. A drawdown event is recorded when
the decline from a peak to a trough exceeds a user-defined percentage.

Outputs an HTML file containing all drawdown events within the given date range.
"""
import argparse
import yfinance as yf
import pandas as pd
from datetime import date

def drawdowns_from_last_peak(symbol, start, end, threshold):
    """
    Calculate drawdown events for a financial instrument.

    A drawdown occurs when the price falls from a peak to a lower trough.
    This function tracks the running peak, detects drawdowns that exceed
    a given threshold, and returns a DataFrame summarizing each event.

    Parameters
    ----------
    symbol : str
        Ticker symbol to retrieve price data for.
    start : str
        Start date in 'YYYY-MM-DD' format.
    end : str
        End date in 'YYYY-MM-DD' format.
    threshold : float
        Minimum drawdown percentage required for an event to be recorded.

    Returns
    -------
    pandas.DataFrame
        Table with columns:
            - peak_date (dd-mm-yyyy)
            - trough_date (dd-mm-yyyy)
            - peak_value
            - trough_value
            - max_drawdown (percentage string)
    """
    data = yf.download(symbol, start=start, end=end, progress=False, auto_adjust=True)
    close = data["Close"].squeeze("columns").dropna().sort_index()

    events = []
    peak_date = close.index[0]
    peak_value = close.iloc[0]
    trough_date = peak_date
    trough_value = peak_value

    for date, price in close.items():
        if price > peak_value:
            if trough_value < peak_value:
                max_dd = (peak_value - trough_value) / peak_value
                if max_dd * 100 >= threshold:
                    events.append({
                        "peak_date": peak_date.strftime("%d-%m-%Y"),
                        "trough_date": trough_date.strftime("%d-%m-%Y"),
                        "peak_value": round(float(peak_value), 2),
                        "trough_value": round(float(trough_value), 2),
                        "max_drawdown": f"{round(max_dd*100, 2)}%"
                    })
            peak_date, peak_value = date, price
            trough_date, trough_value = date, price
        else:
            if price < trough_value:
                trough_date, trough_value = date, price

    # Final check
    if trough_value < peak_value:
        max_dd = (peak_value - trough_value) / peak_value
        if max_dd * 100 >= threshold:
            events.append({
                "peak_date": peak_date.strftime("%d-%m-%Y"),
                "trough_date": trough_date.strftime("%d-%m-%Y"),
                "peak_value": round(float(peak_value), 2),
                "trough_value": round(float(trough_value), 2),
                "max_drawdown": f"{round(max_dd*100, 2)}%"
            })

    return pd.DataFrame(events)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find drawdowns over a period.")
    parser.add_argument("--symbol", default="^GSPC", help="Ticker, (default: ^GSPC)")
    parser.add_argument("--start", default="2024-01-01", help="Start date YYYY-MM-DD (default: 2024-01-01)")
    parser.add_argument("--end", default=date.today().strftime("%Y-%m-%d"), help="End date YYYY-MM-DD (default: today)")
    parser.add_argument("--threshold", type=float, default=4.0, help="Minimum drawdown percentage (default: 4.0)")
    args = parser.parse_args()

    df = drawdowns_from_last_peak(args.symbol, args.start, args.end, args.threshold)
    filename = f"Drawdowns_{args.symbol}_from_{args.start}_to_{args.end}.html"
    df.to_html(filename, index=False)
    print(df)
