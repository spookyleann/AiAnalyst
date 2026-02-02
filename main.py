import tkinter as tk
from tkinter import ttk
import yfinance as yf
import pandas as pd
import numpy as np
from simpleynews import SimpleYNews
from textblob import TextBlob

# ---------------- TECHNICAL INDICATORS ---------------- #

def compute_sma(df, window=20):
    return df["Close"].rolling(window).mean()

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ---------------- DATA FETCH ---------------- #

def get_stock_data(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="6mo")
    info = ticker.info
    return hist, info

def fetch_news(symbol):
    try:
        news = SimpleYNews.Ticker(symbol)
        return news.news[:5]
    except:
        return []

def analyze_sentiment(news):
    scores = []
    for item in news:
        polarity = TextBlob(item.get("title", "")).sentiment.polarity
        scores.append(polarity)
    return round(sum(scores) / len(scores), 3) if scores else 0

# ---------------- GUI ACTION ---------------- #

def analyze():
    symbol = ticker_entry.get().upper()
    output.delete("1.0", tk.END)

    try:
        df, info = get_stock_data(symbol)

        df["SMA20"] = compute_sma(df)
        df["RSI"] = compute_rsi(df["Close"])

        news = fetch_news(symbol)
        sentiment = analyze_sentiment(news)

        output.insert(tk.END, f"📊 {info.get('shortName', symbol)} ({symbol})\n")
        output.insert(tk.END, f"Price: ${info.get('currentPrice', 'N/A')}\n")
        output.insert(tk.END, f"Market Cap: {info.get('marketCap', 'N/A')}\n\n")

        output.insert(tk.END, "📈 Technicals\n")
        output.insert(tk.END, f"SMA(20): {df['SMA20'].iloc[-1]:.2f}\n")
        output.insert(tk.END, f"RSI(14): {df['RSI'].iloc[-1]:.2f}\n\n")

        output.insert(tk.END, "📰 News\n")
        for item in news:
            output.insert(tk.END, f"- {item.get('title')}\n")

        output.insert(tk.END, f"\n🧠 Sentiment Score: {sentiment}")

    except Exception as e:
        output.insert(tk.END, f"Error: {e}")

# ---------------- GUI SETUP ---------------- #

root = tk.Tk()
root.title("AI Company Analyzer")
root.geometry("800x600")

frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(frame, text="Ticker Symbol").pack()
ticker_entry = ttk.Entry(frame, width=15)
ticker_entry.pack()

ttk.Button(frame, text="Analyze", command=analyze).pack(pady=5)

output = tk.Text(frame, wrap=tk.WORD)
output.pack(fill=tk.BOTH, expand=True)

root.mainloop()