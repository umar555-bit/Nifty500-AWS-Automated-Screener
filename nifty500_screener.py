#!/usr/bin/env python3
# ======================================================================
# NIFTY 500 SCREENER — EC2 VERSION (AUTOMATED 2 PM IST, CLEAN LOGS)
# ======================================================================

import pandas as pd, numpy as np, yfinance as yf, requests, io, time, warnings, boto3
from datetime import datetime, date
from collections import Counter
warnings.filterwarnings("ignore")

# ========== CONFIG ==========
MIN_PRICE = 50
MIN_RSI = 50
MIN_VOL_AVG = 500_000
PERIOD = "3mo"
INTERVAL = "1d"
OUTPUT_FILE = "/home/ec2-user/nifty500_results.csv"
AWS_REGION = "ap-south-1"
EMAIL_TO = "umarmateenzhcetamu@gmail.com"
EMAIL_FROM = "umarmateenzhcetamu@gmail.com"
TG_TOKEN = ""
TG_CHAT = ""
# ============================

def is_weekend():
    return datetime.now().weekday() >= 5

def is_nse_holiday_today():
    try:
        r = requests.get("https://www.nseindia.com/api/holiday-master?type=trading",
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        data = r.json()
        today = date.today().isoformat()
        dates = set()
        for k in ["CM", "FO", "tradingHolidayList", "settlementHolidayList"]:
            if k in data and isinstance(data[k], list):
                for item in data[k]:
                    for key in ("tradingDate", "date"):
                        if key in item:
                            raw = item[key]
                            for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%d-%m-%Y"):
                                try:
                                    dt = datetime.strptime(raw, fmt).date()
                                    dates.add(dt.isoformat())
                                    break
                                except:
                                    pass
        return today in dates
    except Exception:
        return False

# ===== Fetch Nifty 500 tickers =====
def get_nifty500(retries=2, timeout=6):
    url = "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv"
    headers = {"User-Agent": "Mozilla/5.0"}
    for attempt in range(1, retries + 1):
        try:
            print(f"Attempt {attempt}: fetching Nifty500…")
            r = requests.get(url, headers=headers, timeout=timeout)
            r.raise_for_status()
            df = pd.read_csv(io.StringIO(r.text))
            if "Symbol" not in df.columns:
                raise ValueError("Bad CSV format")
            symbols = [s.strip() + ".NS" for s in df["Symbol"].dropna().unique()]
            print(f"Loaded {len(symbols)} symbols from Nifty500.")
            return symbols
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            time.sleep(1)
    print("Fallback list active.")
    return ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS', 'ITC.NS', 'SBIN.NS']

# ===== Indicators =====
def compute_indicators(df):
    if df.empty or len(df) < 55:
        return None
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["Vol_SMA20"] = df["Volume"].rolling(20).mean()
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    df["RSI"] = 100 - (100 / (1 + gain / loss))
    df.dropna(inplace=True)
    latest, prev = df.iloc[-1], df.iloc[-2]
    return {
        "close": float(latest["Close"]),
        "volume": float(latest["Volume"]),
        "sma20": float(latest["SMA20"]),
        "sma50": float(latest["SMA50"]),
        "vol_sma20": float(latest["Vol_SMA20"]),
        "rsi": float(latest["RSI"]),
        "prev_high": float(prev["High"]),
    }

def apply_rules(ticker, d):
    failed = []
    if d["close"] <= MIN_PRICE: failed.append("Price ≤ 50")
    if d["volume"] <= d["vol_sma20"]: failed.append("Volume ≤ Avg")
    if d["sma20"] <= d["sma50"]: failed.append("20MA ≤ 50MA")
    if d["rsi"] <= MIN_RSI: failed.append("RSI ≤ 50")
    if d["close"] <= d["sma50"]: failed.append("Price ≤ 50MA")
    if d["close"] <= d["prev_high"]: failed.append("No Breakout")
    if d["vol_sma20"] <= MIN_VOL_AVG: failed.append("Low Liquidity")
    passed = len(failed) == 0
    return dict(ticker=ticker, **d, passes=passed, failed=", ".join(failed) if failed else "All Pass")

# ===== Email via AWS SES =====
def send_email_via_ses(matches_df):
    if matches_df.empty:
        print("No matches to email.")
        return
    ses = boto3.client("ses", region_name=AWS_REGION)
    subject = f"Nifty500 Screener — {date.today().isoformat()} ({len(matches_df)} matches)"
    head = matches_df[["ticker", "close", "rsi", "volume"]].head(15).copy()
    head["close"] = head["close"].map(lambda x: f"₹{x:,.2f}")
    head["rsi"] = head["rsi"].map(lambda x: f"{x:.1f}")
    head["volume"] = head["volume"].map(lambda x: f"{int(x):,}")
    body = [
        f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST",
        f"Matches: {len(matches_df)}",
        "",
        head.to_string(index=False),
        "",
        "Full CSV saved on EC2: nifty500_results.csv"
    ]
    try:
        ses.send_email(
            Source=EMAIL_FROM,
            Destination={"ToAddresses": [EMAIL_TO]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": "\n".join(body)}}
            }
        )
        print(f"SES email sent to {EMAIL_TO}")
    except Exception as e:
        print(f"SES email failed: {e}")

# ===== Telegram =====
def send_telegram(matches_df):
    if not TG_TOKEN or not TG_CHAT or matches_df.empty:
        return
    head = matches_df[["ticker", "close", "rsi"]].head(10).copy()
    head["close"] = head["close"].map(lambda x: f"₹{x:,.2f}")
    head["rsi"] = head["rsi"].map(lambda x: f"{x:.1f}")
    text = f"Nifty500 Screener {date.today().isoformat()}\nMatches: {len(matches_df)}\n\n"
    text += head.to_string(index=False)
    try:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                      data={"chat_id": TG_CHAT, "text": text})
        print("Telegram notification sent.")
    except Exception as e:
        print(f"Telegram failed: {e}")

# ===== Main Logic =====
def main():
    if is_weekend() or is_nse_holiday_today():
        print("Market closed. Exiting.")
        return

    tickers = get_nifty500()
    print(f"\nTotal tickers: {len(tickers)}")
    results = []
    t0 = time.time()

    for t in tickers:
        try:
            df = yf.download(t, period=PERIOD, interval=INTERVAL,
                             auto_adjust=True, progress=False, threads=False)
            if df.empty:
                continue
            ind = compute_indicators(df)
            if ind:
                results.append(apply_rules(t, ind))
        except Exception:
            continue

    df = pd.DataFrame(results)
    if df.empty:
        print("No data processed.")
        return

    matches = df[df["passes"]]
    print(f"Scan completed in {time.time() - t0:.1f}s | Matches: {len(matches)}")

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Results saved: {OUTPUT_FILE}")

    if not matches.empty:
        send_email_via_ses(matches)
        send_telegram(matches)
    else:
        print("No stocks met all 7 conditions.")

if __name__ == "__main__":
    main()

# ===============================================================
# S3 UPLOAD + EC2 AUTO SHUTDOWN
# ===============================================================
import boto3
import requests
from datetime import datetime

def upload_to_s3():
    try:
        s3 = boto3.client("s3", region_name="ap-south-1")
        today = datetime.now().strftime("%Y-%m-%d")
        s3.upload_file(
            "/home/ec2-user/nifty500_results.csv",
            "nifty500-reports-umar",  # your bucket name
            f"reports/nifty500_{today}.csv"
        )
        print("Results uploaded to S3 successfully.")
    except Exception as e:
        print(f"S3 upload failed: {e}")

def stop_ec2_after_completion():
    try:
        instance_id = "i-0383579c1c97b6d38"  # your EC2 ID
        ec2 = boto3.client("ec2", region_name="ap-south-1")
        ec2.stop_instances(InstanceIds=[instance_id])
        print(f"EC2 {instance_id} stopped successfully after completion.")
    except Exception as e:
        print(f"EC2 auto-stop failed: {e}")

upload_to_s3()
stop_ec2_after_completion()
