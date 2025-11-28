#!/usr/bin/python3
"""
Drawdown Tracker

This script downloads historical price data for a financial instrument,
calculates the most recent drawdown from the peak value, and emails a summary of the
results. It uses Yahoo Finance (yfinance) for data retrieval and Gmail SMTP for
sending notifications.
"""

import yfinance as yf
import smtplib
from email.mime.multipart import MIMEMultipart
from datetime import date
import json
import os
import logging
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(script_dir, "drawdown_tracker.log")

logger = logging.getLogger("DrawdownTracker")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%d-%m-%Y %H:%M:%S")

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def last_drawdown(symbol):
    """
    Calculate the most recent drawdown for a symbol.

    Parameters
    ----------
    symbol : str
        The ticker symbol (e.g., "^GSPC").

    Returns
    -------
    dict
        A dictionary containing:
        - peak_date (str): Date of the highest closing price.
        - peak_value (float): Highest closing price.
        - current_date (str): Date of the latest price.
        - current_price (float): Latest closing price.
        - drawdown (float): Percentage drop from the peak.
    """
    try:
        data = yf.download(symbol, period="max", progress=False, auto_adjust=True)
        close = data["Close"].squeeze("columns").dropna().sort_index()

        peak_val = close.max()
        current_price = close.iloc[-1]

        logger.info(f"Calculated drawdown")

        return {
            "peak_date": close.idxmax().strftime("%d-%m-%Y"),
            "peak_value": round(float(peak_val), 2),
            "current_date": close.index[-1].strftime("%d-%m-%Y"),
            "current_price": round(float(current_price), 2),
            "drawdown": round((peak_val - current_price) / peak_val * 100, 2),
        }
    except Exception as e:
        logger.error(f"Error calculating drawdown for {symbol}: {e}")

def send_email(dd, config_file="config.json"):
    """
    Send a drawdown summary email using Gmail SMTP.

    Parameters
    ----------
    dd : dict
        Drawdown dictionary returned from last_drawdown().
    config_file : str, optional
        Path to the configuration file containing:
        {
            "email": "sender@gmail.com",
            "password": "gmail_app_password",
            "recipient": "recipient@gmail.com"
        }

    Notes
    -----
    - Requires an app password (not a normal Gmail password).
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, config_file)
        with open(config_path, "r") as f:
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
    except Exception as e:
        logger.error(f"Error sending email: {e}")

if __name__ == "__main__":
    dd = last_drawdown("^GSPC")
    send_email(dd)
    logger.info("Email sent successfully!")
