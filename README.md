# Nifty500 AWS Automated Stock Screener

This project is an end-to-end **automated stock screening system** built on the **AWS Cloud** using **Python**.  
It identifies high-momentum stocks from the **Nifty 500 index** every trading day at **2 PM IST**, based on key technical indicators.  
The system operates entirely automatically — from scheduling and data processing to email notifications and cloud storage — without manual intervention.

---

## Objective

The purpose of this project is to **automate daily stock analysis** to identify potential breakout and momentum stocks.  
The system runs precisely at **2:00 PM IST**, a period when the market typically consolidates and true intraday momentum becomes visible.  
This timing provides traders and analysts sufficient time to act on insights before market close.

**Key Highlights:**
- Handles **weekends and NSE holidays** (via NSE API)  
- Implements **cloud cost optimization** with auto EC2 shutdown  
- Processes **all 500 stocks in under 2 minutes**

---

## Screening Logic

The Python screener filters stocks based on **seven technical rules**, ensuring that only liquid, trending, and strong momentum stocks are shortlisted.

| Rule | Condition | Purpose |
|------|------------|----------|
| 1 | Price > ₹50 | Avoid illiquid or penny stocks |
| 2 | Volume > 20-day average | Ensure active trading |
| 3 | SMA(20) > SMA(50) | Confirm short-term bullish trend |
| 4 | RSI(14) > 50 | Detect momentum strength |
| 5 | Price > SMA(50) | Confirm long-term uptrend |
| 6 | Price > Previous Day High | Identify breakout signals |
| 7 | 20-Day Average Volume > 500,000 | Maintain sufficient liquidity |

---

## System Architecture

The system is designed using a **fully automated AWS workflow**.

- **Amazon EventBridge** – Scheduled trigger every weekday (Monday–Friday) at **2:00 PM IST** (`cron(30 8 ? * MON-FRI *)` in UTC).  
- **AWS Lambda (Start Function)** – Initiates the EC2 instance only when required, skipping weekends and holidays.  
- **Amazon EC2** – Runs the Python screener script automatically on startup.  
- **Python Script (`nifty500_screener.py`)** – Fetches data from Yahoo Finance, applies logic, and generates reports.  
- **Amazon S3** – Stores daily CSV reports for long-term access.  
- **Amazon SES** – Sends a summary email containing top momentum stocks.  
- **AWS Lambda (Stop Function)** – Shuts down EC2 after completion to minimize cloud cost.

---

## Data Flow

1. **EventBridge** triggers **Lambda** at 2 PM IST.  
2. **Lambda** checks if it’s a trading day and starts EC2.  
3. **EC2** executes the **Python script** automatically on boot.  
4. The script:
   - Fetches Nifty 500 stock data from **Yahoo Finance**.  
   - Computes **technical indicators (SMA, RSI)**.  
   - Applies **screening rules**.  
   - Saves a **CSV report locally** and uploads to **S3**.  
   - Sends a **summary email** via **SES**.  
5. **Lambda Stop Function** shuts down EC2 to save cost.

---

## AWS Services Used

| Service | Purpose |
|----------|----------|
| **Amazon EventBridge** | Scheduled daily trigger at 2 PM IST |
| **AWS Lambda** | Automates EC2 startup and shutdown |
| **Amazon EC2** | Executes the main Python screener |
| **Amazon S3** | Stores daily stock screening reports |
| **Amazon SES** | Sends summary emails to the user |
| **AWS CloudWatch** | Monitors logs and execution |
| **AWS IAM** | Manages permissions and roles |

---

## Technical Details

- **Programming Language:** Python 3  
- **Libraries Used:** `yfinance`, `pandas`, `numpy`, `requests`, `boto3`  
- **Data Source:** Yahoo Finance / NSE API  
- **Execution Time:** Under 2 minutes for 500 stocks  
- **Deployment Region:** `ap-south-1 (Mumbai)`  
- **Output:** CSV file stored in S3 + summary email via SES  

---



## Performance and Optimization

- **Execution Time:** Under 120 seconds for 500 stocks  
- **Cost Efficiency:** EC2 runs only during processing, then auto-stops  
- **Error Handling:** Gracefully skips delisted or missing tickers  
- **Market Awareness:** Automatically detects weekends and NSE holidays  
- **Data Storage:** Each day’s results saved in a versioned S3 path  

---

## Security and IAM Configuration

| Role | Permissions |
|------|--------------|
| **Lambda Role** | `ec2:DescribeInstances`, `ec2:StartInstances`, `logs:*` |
| **EC2 Role** | `s3:PutObject`, `ses:SendEmail`, `ec2:StopInstances` |
| **S3 Bucket Policy** | Access restricted to EC2 instance role only |

---

## Results Storage

- **S3 Bucket:** `nifty500-reports-umar`  
- **File Path:** `reports/nifty500_<date>.csv`  
- **Retention:** Reports stored indefinitely for analysis and backtesting  

---

---

## Author

**Umar Mateen**  
B.Tech in Engineering (AMU)  
**Data Analyst & Data Engineer**

**Skills:** Python, SQL, Power BI, AWS, Machine Learning, Data Analytics  
**Email:** [umarmateenzhcetamu@gmail.com](mailto:umarmateenzhcetamu@gmail.com)  
**GitHub:** [umar555-bit](https://github.com/umar555-bit)

