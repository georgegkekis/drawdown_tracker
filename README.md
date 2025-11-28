# drawdown_tracker

This repository contains two tools designed to help monitor and analyze market drawdowns.

1. tracker.py

This script sends an email with the current drawdown from the all-time high of a selected instrument.
I run this every morning to receive an automatic notification showing how far below its historical peak the instrument currently is.

2. drawdown_analysis.py

This script analyzes historical price data and reports all drawdowns greater than a specified percentage over a given date range.
I use it to understand the historical behavior of an instrument — specifically, how deep previous drawdowns have been and how often they occur.

---

## 📦 Installation

```bash
git clone https://github.com/georgegkekis/drawdown_tracker.git
cd drawdown_tracker
pip install -r requirements
```
Create a config.json for email credentials:
```
{
  "email": "your_gmail@gmail.com",
  "password": "your_gmail_app_password"
  "recipient" : "your_recipient@gmail.com"
}
```
Use a Gmail App Password (requires 2FA).

## Usage

- python tracker.py [symbol] [start_date] [end_date] [threshold]
- symbol — ticker symbol (default: ^GSPC)
- start_date — format YYYY-MM-DD (default: 2024-01-01)
- end_date — format YYYY-MM-DD or today (default: today)
- threshold — minimum drawdown percentage (default: 5.0)

Example:
```
python3 tracker.py ^GSPC 2024-01-01 today 5.0
python3 tracker.py
```
- python drawdown_analysis.py [symbol] [start_date] [end_date] [threshold]
- symbol  - The market ticker to analyze (e.g., ^GSPC for S&P 500).
- start  - Start date for the analysis in YYYY-MM-DD format.
- end - End date for the analysis in YYYY-MM-DD format.
- threshold - Minimum drawdown percentage to report.

Example:
```
python3 drawdown_analysis.py \
    --symbol ^GSPC \
    --start 2010-01-01 \
    --end 2025-01-01 \
    --threshold 5 \
    --output_file sp500_drawdowns
```

