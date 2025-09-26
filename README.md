# drawdown_tracker

A Python tool for tracking and alerting **drawdowns** (declines from peaks) in financial instruments (e.g. S&P 500). It fetches price data, identifies peak-to-trough events, and can send email alerts with the latest drawdown.

---

## 🚀 Features

- Download historical daily price data (via `yfinance`)
- Identify drawdowns from each new peak (peak → trough)
- Option to set a minimum threshold (e.g. only log drawdowns > 5 %)
- Output results as table / HTML
- Send email alerts with the latest drawdown (peak, trough, current price)
- CLI interface with customizable symbol, date range, threshold

---

## 📦 Installation

```bash
git clone https://github.com/georgegkekis/drawdown_tracker.git
cd drawdown_tracker
pip install -r requirements

Create a config.json for email credentials:

{
  "email": "your_gmail@gmail.com",
  "password": "your_gmail_app_password"
  "recipient" : "your_recipient@gmail.com"
}

Use a Gmail App Password (requires 2FA).

## Usage

- python tracker.py [symbol] [start_date] [end_date] [threshold]
- symbol — ticker symbol (default: ^GSPC)
- start_date — format YYYY-MM-DD (default: 2024-01-01)
- end_date — format YYYY-MM-DD or today (default: today)
- threshold — minimum drawdown percentage (default: 5.0)

Example:
python3 tracker.py ^GSPC 2024-01-01 today 5.0
python3 tracker.py
