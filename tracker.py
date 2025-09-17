import yfinance as yf
import pandas as pd

def drawdowns_from_last_peak(symbol="^GSPC", start="2025-01-01", end="2025-12-31"):
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
        events.append({
            "peak_date": peak_date.strftime("%d-%m-%Y"),
            "trough_date": trough_date.strftime("%d-%m-%Y"),
            "peak_value": round(float(peak_value), 2),
            "trough_value": round(float(trough_value), 2),
            "max_drawdown": f"{round(max_dd*100, 2)}%"
        })

    return pd.DataFrame(events)

if __name__ == "__main__":
    df = drawdowns_from_last_peak("^GSPC", "2024-01-01", "2024-12-31")
    df.to_html("drawdowns.html", index=False)
    print(df)
