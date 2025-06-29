# ✅ MarketSage Full Script – Clean PDF + Strong Filters

import yfinance as yf
import pandas as pd
!pip install yfinance pandas reportlab --quiet
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
import datetime
import requests
from tqdm import tqdm
import time

# === Step 1: Telegram Bot Message ===
# 📬 Telegram Bot Setup
bot_token = '7614155863:AAF3gSot7NRJCsAPfI6w369lAEd23cClj5Q'
chat_id = '766461436'

message = "\U0001F680 Hello Surya! Your MarketSage bot is now LIVE! \U0001F4C8\U0001F525"
requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}")

# === Step 2: Index & Sector Summary ===
indices = {
    "Nifty 50": "^NSEI",
    "Bank Nifty": "^NSEBANK",
    "Fin Nifty": "^CNXFIN"
}

print("\n\U0001F4C8 Market Index Summary:")
for name, symbol in indices.items():
    data = yf.Ticker(symbol).history(period="2d")
    if len(data) >= 2:
        today, prev = data['Close'].iloc[-1], data['Close'].iloc[-2]
        chg, pct = today - prev, (today - prev) / prev * 100
        print(f"➡️ {name}: {today:.2f} ({chg:+.2f}, {pct:+.2f}%)")

sector_indices = {
    'Auto': '^CNXAUTO', 'Banking': '^NSEBANK', 'FMCG': '^CNXFMCG',
    'IT': '^CNXIT', 'Metal': '^CNXMETAL', 'Pharma': '^CNXPHARMA',
    'Energy': '^CNXENERGY', 'Infrastructure': '^CNXINFRA',
    'Media': '^CNXMEDIA'
}

print("\n\U0001F4CA Sector Performance (Daily):")
for name, symbol in sector_indices.items():
    try:
        data = yf.Ticker(symbol).history(period="2d")
        today, prev = data['Close'].iloc[-1], data['Close'].iloc[-2]
        chg, pct = today - prev, (today - prev) / prev * 100
        print(f"{name:20} ➜ {today:.2f} ({chg:+.2f}, {pct:+.2f}%)")
    except:
        print(f"{name:20} ➜ ❌ Data Unavailable")

# === Step 3: Load Nifty 500 ===
nifty500_url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
nifty500_df = pd.read_csv(nifty500_url)
nifty500_df['Symbol'] = nifty500_df['Symbol'].apply(lambda x: x.strip() + '.NS')
nifty500_tickers = nifty500_df['Symbol'].tolist()
print(f"\n✅ Loaded {len(nifty500_tickers)} Nifty 500 stock tickers")

# === Step 3: SMA & ATH Scanner ===
buy_signals = []

for ticker in tqdm(nifty500_tickers, desc="Scanning Stocks"):
    try:
        stock = yf.Ticker(ticker)

        # Get 5 years of data for ATH check
        hist = stock.history(period="5y")

        if hist.empty or 'Close' not in hist.columns:
            continue

        # Calculate SMA50 and SMA200
        hist['SMA50'] = hist['Close'].rolling(window=50).mean()
        hist['SMA200'] = hist['Close'].rolling(window=200).mean()

        latest = hist.iloc[-1]
        sma50 = latest['SMA50']
        sma200 = latest['SMA200']
        latest_close = latest['Close']
        ath = hist['Close'].max()

        if pd.notna(sma50) and pd.notna(sma200) and sma50 > sma200:
            is_ath = "Yes ✅" if abs(latest_close - ath) < 0.5 else ""
            buy_signals.append({
                'Ticker': ticker,
                'SMA50': round(sma50, 2),
                'SMA200': round(sma200, 2),
                'Latest Close': round(latest_close, 2),
                'All Time High': is_ath,
                'Signal': 'BUY'
            })

        time.sleep(0.05)

    except Exception as e:
        print(f"❌ Error for {ticker}: {e}")
        continue

df_signals = pd.DataFrame(buy_signals)
print(f"\n✅ Final Buy Signals: {len(df_signals)} stocks")
print(df_signals.head())

# === Step 4: Generate PDF ===
def create_pdf(df, filename="marketsage_report.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    title = f"📄 MarketSage BUY Report – {datetime.datetime.now().strftime('%d-%b-%Y')}"
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 12))

    headings = ['Ticker', 'Latest Close', 'SMA50', 'SMA200', 'Signal', 'All Time High']
    # Convert list of dictionaries to list of lists, ensuring correct order
    data = [[d['Ticker'], d['Latest Close'], d['SMA50'], d['SMA200'], d['Signal'], d['All Time High']] for d in df]
    table_data = [headings] + data

    table = Table(table_data, colWidths=[90]*6)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
    ]))

    story.append(table)
    doc.build(story)

create_pdf(buy_signals, "marketsage_report.pdf")

if os.path.exists("marketsage_report.pdf"):
    print("✅ PDF File Exists – Ready to send.")
    send_pdf_to_telegram("marketsage_report.pdf")
else:
    print("❌ PDF File Missing – Something went wrong!")


# === Step 5: Send to Telegram ===
def send_pdf_to_telegram(file_path):
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': chat_id, 'caption': "📊 MarketSage Technical Buy Signals – SMA + ATH"}
        response = requests.post(url, files=files, data=data)
    print("✅ Sent PDF to Telegram")

send_pdf_to_telegram("marketsage_report.pdf")
