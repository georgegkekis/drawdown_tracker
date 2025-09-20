import yfinance as yf
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
import json

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

def send_email(df, report_html, config_file="config.json"):
    with open(config_file, "r") as f:
        config = json.load(f)

    sender_email = config["email"]
    sender_password = config["password"]
    recipient_email = config["recipient"]

    last_event = df.tail(1)
    dd = last_event.iloc[0]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"S&P 500 Drawdown {dd['max_drawdown']} (from {dd['peak_date']} to {dd['trough_date']})"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    body = MIMEText(report_html, "html")
    msg.attach(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

if __name__ == "__main__":
    df = drawdowns_from_last_peak("^GSPC", "2024-01-01", date.today().strftime("%Y-%m-%d"), 5.0)
    report_html = df.to_html(index=False)
    send_email(df, report_html)
    print("Email sent successfully!")
