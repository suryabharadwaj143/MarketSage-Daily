# 📈 MarketSage - Daily Stock Market Scanner & Telegram Bot 🧠📊

MarketSage is an AI-powered stock analysis bot that scans the entire Nifty 500 daily and sends a clean PDF report to Telegram at 5:30 PM IST — completely automated using GitHub Actions.

## 🚀 Features

- 📊 **Scans all Nifty 500 stocks**
- 💰 **Filters fundamentally strong stocks**
  - Technical signal: `SMA50 > SMA200`
  - Optional: All-Time High detection
- 📈 **Generates Buy Signals**
- 📄 **Creates PDF Report** with a table view
- 🤖 **Sends PDF to Telegram** daily via Bot
- ⚙️ **Fully automated with GitHub Actions**

## 📌 Sample Output

| Ticker       | SMA50  | SMA200 | Latest Close | All Time High | Signal |
|--------------|--------|--------|---------------|----------------|--------|
| RELIANCE.NS  | 2710   | 2650   | 2750          | Yes            | BUY    |

## 🛠️ Tech Stack

- Python
- yFinance
- Pandas
- ReportLab (PDF)
- GitHub Actions (CI/CD)
- Telegram Bot API

## 📦 Installation

```bash
pip install -r requirements.txt
python marketsage.py

## ✍️ **Author**
Made with ❤️ by [@suryabharadwaj143](https://github.com/suryabharadwaj143)
