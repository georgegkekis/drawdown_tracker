import yfinance as yf
import smtplib
from email.mime.multipart import MIMEMultipart
from datetime import date
import json

def last_drawdown(symbol, start, end):
    data = yf.download(symbol, start=start, end=end, progress=False, auto_adjust=True)
    close = data["Close"].squeeze("columns").dropna().sort_index()

    peak_val = close.max()
    current_price = close.iloc[-1]

    return {
        "peak_date": close.idxmax().strftime("%d-%m-%Y"),
        "peak_value": round(float(peak_val), 2),
        "current_date": close.index[-1].strftime("%d-%m-%Y"),
        "current_price": round(float(current_price), 2),
        "drawdown": round((peak_val - current_price) / peak_val * 100, 2),
    }

def send_email(dd, config_file="config.json"):
    with open(config_file, "r") as f:
        config = json.load(f)

    sender_email = config["email"]
    sender_password = config["password"]
    recipient_email = config["recipient"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"S&P500 Drawdown:{dd['drawdown']}% (from {dd['peak_date']} to {dd['current_date']})Last Peak:{dd['peak_value']} Today's Value:{dd['current_price']} "
    msg["From"] = sender_email
    msg["To"] = recipient_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

if __name__ == "__main__":
    dd = last_drawdown("^GSPC", "2024-01-01", date.today().strftime("%Y-%m-%d"))
    #report_html = df.to_html(index=False)
    send_email(dd)
    print("Email sent successfully!")
