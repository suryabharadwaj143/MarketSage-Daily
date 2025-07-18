# ✅ MarketSage Final Script – Clean PDF + Strong Filters (SMA + ATH)
import yfinance as yf
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import datetime
import requests
from tqdm import tqdm
import time
import os



# === Step 1: Telegram Bot Message ===

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]



message = ("\U0001F680 Hello! MarketSage Daily Report is being generated. Please wait...")
requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}")


# === Step 2: Market Index Summary ===
print("\n\U0001F4C8 Market Index Summary:")
indices = {
    "Nifty 50": "^NSEI",
    "Bank Nifty": "^NSEBANK"
}
index_summary = []
for name, symbol in indices.items():
    data = yf.Ticker(symbol).history(period="2d")
    if len(data) >= 2:
        today, prev = data['Close'].iloc[-1], data['Close'].iloc[-2]
        chg, pct = today - prev, (today - prev) / prev * 100
        print(f"➡️ {name}: {today:.2f} ({chg:+.2f}, {pct:+.2f}%)")
        index_summary.append([name, f"{today:.2f}", f"{chg:+.2f}", f"{pct:+.2f}%"])

# === Step 3: Sector Performance ===
print("\n\U0001F4CA Sector Performance (Daily):")
sector_indices = {
    'Auto': '^CNXAUTO', 'Banking': '^NSEBANK', 'FMCG': '^CNXFMCG',
    'IT': '^CNXIT', 'Metal': '^CNXMETAL', 'Pharma': '^CNXPHARMA',
    'Energy': '^CNXENERGY', 'Infrastructure': '^CNXINFRA', 'Media': '^CNXMEDIA'
}
sector_data = []
for name, symbol in sector_indices.items():
    try:
        data = yf.Ticker(symbol).history(period="2d")
        today, prev = data['Close'].iloc[-1], data['Close'].iloc[-2]
        chg, pct = today - prev, (today - prev) / prev * 100
        print(f"{name:15} ➔ {today:.2f} ({chg:+.2f}, {pct:+.2f}%)")
        sector_data.append([name, f"{today:.2f}", f"{chg:+.2f}", f"{pct:+.2f}%"])
    except:
        print(f"{name:15} ➔ ❌ Data Unavailable")

# === Step 4: Top Gainers & Losers ===
print("\n\U0001F525 Top 5 Gainers & Losers")
nifty500_df = pd.read_csv("https://archives.nseindia.com/content/indices/ind_nifty500list.csv")
nifty500_df['Symbol'] = nifty500_df['Symbol'].apply(lambda x: x.strip() + '.NS')
nifty500_tickers = nifty500_df['Symbol'].tolist()

price_data = yf.download(nifty500_tickers, period="2d", interval="1d", group_by='ticker', threads=True, progress=False)
gainers_losers = []
for ticker in nifty500_tickers:
    try:
        df = price_data[ticker]['Close']
        if len(df) == 2:
            prev_close, curr_close = df.iloc[0], df.iloc[1]
            pct_change = ((curr_close - prev_close) / prev_close) * 100
            if abs(pct_change) < 25:  # Filter out anomalies (splits, data errors)
                gainers_losers.append((ticker, round(curr_close, 2), round(pct_change, 2)))
    except:
        continue

gainers_df = pd.DataFrame(gainers_losers, columns=['Ticker', 'Close', '% Change'])
top_gainers = gainers_df.sort_values(by='% Change', ascending=False).head(5)
top_losers = gainers_df.sort_values(by='% Change').head(5)

print("\nTop 5 Gainers:")
print(top_gainers.to_string(index=False))
print("\nTop 5 Losers:")
print(top_losers.to_string(index=False))

# === Step 5: SMA + ATH BUY SCAN ===
print("\n✅ Loaded", len(nifty500_tickers), "Nifty 500 stock tickers")
buy_signals = []
for ticker in tqdm(nifty500_tickers, desc="Scanning Stocks"):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5y")
        if hist.empty or 'Close' not in hist.columns:
            continue
        hist['SMA50'] = hist['Close'].rolling(window=50).mean()
        hist['SMA200'] = hist['Close'].rolling(window=200).mean()
        latest = hist.iloc[-1]
        sma50, sma200, latest_close = latest['SMA50'], latest['SMA200'], latest['Close']
        ath = hist['Close'].max()

        if pd.notna(sma50) and pd.notna(sma200) and sma50 > sma200:
            is_ath = "Yes ✅" if abs(latest_close - ath) / ath < 0.005 else ""
            buy_signals.append({
                'Ticker': ticker,
                'SMA50': round(sma50, 2),
                'SMA200': round(sma200, 2),
                'Latest Close': round(latest_close, 2),
                'Signal': 'BUY',
                'All Time High': is_ath
            })
        time.sleep(0.05)
    except:
        continue

print("\n✅ Final Buy Signals:", len(buy_signals), "stocks")

# === Step 6: Create PDF ===
def create_pdf(index_summary, sector_data, gainers, losers, buy_data, filename="marketsage_report.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("\U0001F4CA MarketSage Daily Report", styles['Title']))
    story.append(Spacer(1, 12))

    def create_table(title, data, highlight_column_idx=None):
        story.append(Paragraph(title, styles['Heading3']))
        table = Table([data[0]] + data[1:], hAlign='CENTER')
        style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ])
        for i, row in enumerate(data[1:], start=1):
            if highlight_column_idx is not None and isinstance(row[highlight_column_idx], str) and '%' in row[highlight_column_idx] and '+' in row[highlight_column_idx]:
                style.add('BACKGROUND', (highlight_column_idx, i), (highlight_column_idx, i), colors.lightgreen)
        table.setStyle(style)
        story.append(table)
        story.append(Spacer(1, 12))

    if index_summary:
        create_table("Index Summary", [['Index', 'Close', 'Change', '% Change']] + index_summary)
    if sector_data:
        create_table("Sector Performance", [['Sector', 'Close', 'Change', '% Change']] + sector_data, highlight_column_idx=3)
    if not top_gainers.empty:
        create_table("Top 5 Gainers", [['Ticker', 'Close', '% Change']] + top_gainers.values.tolist(), highlight_column_idx=2)
    if not top_losers.empty:
        create_table("Top 5 Losers", [['Ticker', 'Close', '% Change']] + top_losers.values.tolist(), highlight_column_idx=2)
    if buy_data:
        table_data = [['Ticker', 'Latest Close', 'SMA50', 'SMA200', 'Signal', 'All Time High']]
        for d in buy_data:
            table_data.append([
                d['Ticker'], d['Latest Close'], d['SMA50'], d['SMA200'], d['Signal'], d['All Time High']
            ])
        create_table("Technical BUY Signals", table_data)

    doc.build(story)

create_pdf(index_summary, sector_data, top_gainers, top_losers, buy_signals)

# === Step 7: Telegram Send ===
import os
import requests

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
PDF_FILE_PATH = "marketsage_report.pdf"

def send_telegram_pdf():
    print("=== Preparing to send PDF to Telegram ===")
    try:
        with open(PDF_FILE_PATH, "rb") as pdf_file:
            response = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument",
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "caption": "📊 MarketSage Daily Report is here!"
                },
                files={"document": pdf_file}
            )
            print(f"Telegram Response Status: {response.status_code}")
            print(f"Telegram Response: {response.text}")
            response.raise_for_status()
            print("✅ PDF sent to Telegram successfully.")
    except Exception as e:
        print(f"❌ Error sending PDF to Telegram: {e}")


# Call the function
send_telegram_pdf()



