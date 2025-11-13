Nifty500 AWS Automated Stock Screener

This project is an end-to-end automated stock screening system built on the AWS Cloud using Python.
It identifies high-momentum stocks from the Nifty 500 index every trading day at 2 PM IST, based on key technical indicators.
The system operates entirely automatically — from scheduling and data processing to email notifications and cloud storage — without manual intervention.

Objective

The purpose of this project is to automate daily stock analysis to identify potential breakout and momentum stocks.
The system runs precisely at 2:00 PM IST, a period when the market typically consolidates and true intraday momentum becomes visible.
This timing provides traders and analysts sufficient time to act on the insights before market close.

The project also intelligently handles:

Weekends and NSE holidays (detected via the NSE API)

Cloud cost optimization (automatic EC2 shutdown)

Performance efficiency (processes all 500 stocks in under 2 minutes)

Screening Logic

The Python screener filters stocks based on seven technical rules, ensuring that only liquid, trending, and strong momentum stocks are shortlisted.

Rule	Condition	Purpose
1	Price > ₹50	Avoid illiquid or penny stocks
2	Volume > 20-day average	Ensure active trading
3	SMA(20) > SMA(50)	Confirm short-term bullish trend
4	RSI(14) > 50	Detect momentum strength
5	Price > SMA(50)	Confirm long-term uptrend
6	Price > Previous Day High	Identify breakout signals
7	20-Day Average Volume > 500,000	Maintain sufficient liquidity
System Architecture

The system is designed using a fully automated AWS workflow.

Amazon EventBridge – A scheduled rule triggers every weekday (Monday–Friday) at 2:00 PM IST (cron(30 8 ? * MON-FRI *) in UTC).

AWS Lambda (Start Function) – Initiates the EC2 instance only when required, skipping weekends and NSE holidays.

Amazon EC2 – Runs the Python screener script automatically on startup.

Python Script (nifty500_screener.py) – Fetches data from Yahoo Finance, applies screening logic, and generates a daily report.

Amazon S3 – Stores the daily CSV file for long-term archival and access.

Amazon SES (Simple Email Service) – Sends a summary email containing top momentum stocks.

AWS Lambda (Stop Function) – Stops the EC2 instance after completion to minimize cloud cost.

Data Flow

EventBridge scheduler triggers Lambda at 2 PM IST.

Lambda function checks if it is a trading day and starts the EC2 instance.

EC2 instance executes the Python script upon boot.

The script:

Fetches price and volume data for all Nifty 500 stocks.

Computes technical indicators such as SMA and RSI.

Filters stocks based on the defined screening criteria.

Generates and saves a CSV report locally.

Uploads the report to an S3 bucket.

Sends an email summary through Amazon SES.

Once processing completes, the EC2 instance shuts down automatically.

AWS Services Used
Service	Purpose
Amazon EventBridge	Scheduled daily trigger at 2 PM IST
AWS Lambda	Automates EC2 startup and shutdown
Amazon EC2	Executes Python screener script
Amazon S3	Stores daily reports securely
Amazon SES	Sends stock summary emails
AWS CloudWatch	Logs monitoring and error tracking
AWS IAM	Access management and permissions control
Technical Details

Programming Language: Python 3

Libraries Used: yfinance, pandas, numpy, requests, boto3

Data Source: Yahoo Finance / NSE API

Average Execution Time: Under 2 minutes for 500 stocks

Deployment Region: ap-south-1 (Mumbai)

Output Format: CSV stored in S3 and summary email sent via SES

Output Example

Email Summary:

Nifty500 Screener — 2025-11-10
Matches: 8

TICKER       PRICE     RSI     VOLUME
RELIANCE.NS  ₹2755.40  62.4    8,234,200
TCS.NS       ₹3802.75  58.3    4,652,110
HDFCBANK.NS  ₹1568.10  55.9    7,842,330
...
Full CSV report uploaded to S3: nifty500-reports-umar/reports/nifty500_2025-11-10.csv

Performance and Optimization

Execution Time: Under 120 seconds for 500 stocks.

Cost Optimization: EC2 instance is active only during processing; stopped automatically afterward.

Error Handling: Skips delisted or missing tickers to prevent runtime errors.

Market Awareness: Automatically detects weekends and official NSE holidays.

Data Persistence: Stores each day’s results in a versioned S3 folder.

Security and IAM
Role	Permissions
Lambda Role	ec2:DescribeInstances, ec2:StartInstances, logs:*
EC2 Role	s3:PutObject, ses:SendEmail, ec2:StopInstances
S3 Bucket Policy	Restricted access to EC2 instance role only

Results Storage

S3 Bucket: nifty500-reports-umar

Report Path: reports/nifty500_<date>.csv

Retention: Reports stored indefinitely for performance tracking and analysis.

Author

Umar Mateen
B.Tech in Engineering (AMU)
Data Analyst & Data Engineer
Skills: Python, SQL, Power BI, AWS, Machine Learning, Data Analytics
Email: umarmateenzhcetamu@gmail.com

GitHub: umar555-bit
