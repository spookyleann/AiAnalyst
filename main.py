import tkinter as tk
from tkinter import ttk
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from simpleynews import SimpleYNews
from textblob import TextBlob
from stonksapi import StonksApi

# ---------- DATA & ANALYSIS FUNCTIONS ----------

def get_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="6mo")
        info = ticker.info
        return hist, info
    except Exception as e:
        return None, {"Error": str(e)}

def compute_indicators(df):
    df["SMA20"] = ta.sma(df["Close"], length=20)
    df["RSI"] = ta.rsi(df["Close"], length=14)
    return df

def fetch_news(symbol):
    try:
        news_provider = SimpleYNews.Ticker(symbol)
        return news_provider.news
    except Exception as e:
        return [{"title": f"Error fetching news: {e}"}]

def sentiment_score(headlines):
    scores = []
    for h in headlines:
        text = h.get("title", "")
        sentiment = TextBlob(text).sentiment.polarity
        scores.append(sentiment)
    return sum(scores) / len(scores) if scores else 0

# ---------- GUI ----------

def analyze():
    symbol = ticker_entry.get().upper()
    output_text.delete("1.0", tk.END)

    # Stock
    hist, info = get_stock_data(symbol)
    if "Error" in info:
        output_text.insert(tk.END, f"Error: {info['Error']}\n")
        return

    output_text.insert(tk.END, f"=== {info.get('shortName', symbol)} ({symbol}) ===\n")
    output_text.insert(tk.END, f"Current Price: {info.get('currentPrice', 'N/A')}\n")
    output_text.insert(tk.END, f"Market Cap: {info.get('marketCap', 'N/A')}\n\n")

    # Technical
    df = compute_indicators(hist.copy())
    output_text.insert(tk.END, "=== Technical Indicators ===\n")
    output_text.insert(tk.END, f"Last Close: {df['Close'][-1]:.2f}\n")
    output_text.insert(tk.END, f"20-Day SMA: {df['SMA20'][-1]:.2f}\n")
    output_text.insert(tk.END, f"RSI: {df['RSI'][-1]:.2f}\n\n")

    # News
    output_text.insert(tk.END, "=== Latest News ===\n")
    news_items = fetch_news(symbol)
    for n in news_items[:5]:
        title = n.get("title", "No title")
        output_text.insert(tk.END, f"{title}\n")

    # Sentiment
    score = sentiment_score(news_items[:5])
    output_text.insert(tk.END, f"\nAvg Sentiment Score: {score:.3f}\n")

# ---------- TKINTER SETUP ----------

root = tk.Tk()
root.title("AI Company Analysis")
root.geometry("800x600")

frame = ttk.Frame(root, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

ticker_label = ttk.Label(frame, text="Enter Ticker Symbol:")
ticker_label.pack()
ticker_entry = ttk.Entry(frame, width=15)
ticker_entry.pack()

analyze_btn = ttk.Button(frame, text="Analyze", command=analyze)
analyze_btn.pack()

output_text = tk.Text(frame, wrap=tk.WORD)
output_text.pack(fill=tk.BOTH, expand=True)

root.mainloop()