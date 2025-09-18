import yfinance as yf
import pandas as pd
import argparse

def drawdowns_from_last_peak(symbol, start, end, threshold):
    data = yf.download(symbol, start=start, end=end, progress=False, auto_adjust=True)
    close = data["Close"].squeeze("columns").dropna().sort_index()

    events = []
    peak_date = close.index[0]
    peak_value = close.iloc[0]
    trough_date = peak_date
    trough_value = peak_value

    for date, price in close.items():
        if price > peak_value:
            # New peak found → record previous drawdown if any
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
            # Reset peak
            peak_date, peak_value = date, price
            trough_date, trough_value = date, price
        else:
            # Update trough
            if price < trough_value:
                trough_date, trough_value = date, price

    # Final check in case it never recovered from the trough
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
    parser = argparse.ArgumentParser(description="Find drawdowns for a financial instrument.")
    parser.add_argument("symbol", nargs="?", default="^GSPC", help="Ticker symbol (default: ^GSPC)")
    parser.add_argument("start", nargs="?", default="2025-01-01", help="Start date YYYY-MM-DD (default: 2024-01-01)")
    parser.add_argument("end", nargs="?", default="2025-12-31", help="End date YYYY-MM-DD (default: 2024-12-31)")
    parser.add_argument("threshold", nargs="?", type=float, default=2.0, help="Minimum drawdown percentage (default: 2.0)")

    args = parser.parse_args()

    df = drawdowns_from_last_peak(args.symbol, args.start, args.end, args.threshold)
    df.to_html("drawdowns.html", index=False)
    print(df)
