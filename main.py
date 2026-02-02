import tkinter as tk
from tkinter import ttk
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from simpleynews import SimpleYNews
from textblob import TextBlob

# ---------------- TECHNICALS ---------------- #

def compute_sma(series, window=20):
    return series.rolling(window).mean()

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def support_resistance(series, window=20):
    support = series.rolling(window).min().iloc[-1]
    resistance = series.rolling(window).max().iloc[-1]
    return support, resistance

# ---------------- DATA ---------------- #

def get_stock_data(symbol):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="6mo")
    info = ticker.info
    return df, info

def fetch_news(symbol):
    try:
        news = SimpleYNews.Ticker(symbol)
        return news.news[:6]
    except:
        return []

def sentiment_score(news):
    scores = [
        TextBlob(n.get("title", "")).sentiment.polarity
        for n in news
    ]
    return round(np.mean(scores), 3) if scores else 0

# ---------------- ANALYSIS ---------------- #

def trend_score(price, sma, rsi):
    score = 0

    if price > sma:
        score += 40
    if rsi > 55:
        score += 30
    if rsi > 65:
        score += 10
    if rsi < 45:
        score -= 20

    if score >= 60:
        label = "Bullish"
    elif score >= 40:
        label = "Neutral"
    else:
        label = "Bearish"

    return label, max(min(score, 100), 0)

def risk_score(rsi, sentiment):
    risk = 50
    if rsi > 70 or rsi < 30:
        risk += 20
    if abs(sentiment) > 0.3:
        risk += 10
    return min(risk, 100)

def investment_thesis(trend, sentiment, risk):
    if trend == "Bullish" and sentiment > 0:
        return "Positive momentum with supportive sentiment. Favorable risk-reward."
    if trend == "Bearish" and sentiment < 0:
        return "Negative trend reinforced by poor sentiment. Elevated downside risk."
    return "Mixed signals. Market awaiting confirmation."

# ---------------- GUI ACTION ---------------- #

def analyze():
    symbol = ticker_entry.get().upper()
    output.delete("1.0", tk.END)

    try:
        df, info = get_stock_data(symbol)

        df["SMA20"] = compute_sma(df["Close"])
        df["RSI"] = compute_rsi(df["Close"])

        price = df["Close"].iloc[-1]
        sma = df["SMA20"].iloc[-1]
        rsi = df["RSI"].iloc[-1]

        support, resistance = support_resistance(df["Close"])
        news = fetch_news(symbol)
        sentiment = sentiment_score(news)

        trend, trend_val = trend_score(price, sma, rsi)
        risk = risk_score(rsi, sentiment)
        thesis = investment_thesis(trend, sentiment, risk)

        # ---- OUTPUT ---- #
        output.insert(tk.END, f"📊 {info.get('shortName', symbol)} ({symbol})\n")
        output.insert(tk.END, f"Price: ${price:.2f}\n")
        output.insert(tk.END, f"Market Cap: {info.get('marketCap', 'N/A')}\n\n")

        output.insert(tk.END, "📈 Technicals\n")
        output.insert(tk.END, f"SMA20: {sma:.2f}\n")
        output.insert(tk.END, f"RSI: {rsi:.2f}\n")
        output.insert(tk.END, f"Support: {support:.2f}\n")
        output.insert(tk.END, f"Resistance: {resistance:.2f}\n\n")

        output.insert(tk.END, "📉 Trend Analysis\n")
        output.insert(tk.END, f"Trend: {trend} ({trend_val}/100)\n")
        output.insert(tk.END, f"Risk Score: {risk}/100\n\n")

        output.insert(tk.END, "🧠 AI Investment Thesis\n")
        output.insert(tk.END, thesis + "\n\n")

        output.insert(tk.END, "📰 News\n")
        for n in news:
            output.insert(tk.END, f"- {n.get('title')}\n")

        output.insert(tk.END, f"\nSentiment Score: {sentiment}")

        # ---- CHART ---- #
        plt.figure(figsize=(10, 4))
        plt.plot(df["Close"], label="Close")
        plt.plot(df["SMA20"], label="SMA20")
        plt.axhline(support, linestyle="--", alpha=0.5)
        plt.axhline(resistance, linestyle="--", alpha=0.5)
        plt.title(symbol)
        plt.legend()
        plt.show()

    except Exception as e:
        output.insert(tk.END, f"Error: {e}")

# ---------------- GUI ---------------- #

root = tk.Tk()
root.title("AI Company Analyzer")
root.geometry("900x650")
root.minsize(800, 500)

frame = ttk.Frame(root, padding=12)
frame.grid(row=0, column=0, sticky="nsew")

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# --- Input ---
ttk.Label(frame, text="Ticker Symbol").grid(row=0, column=0, sticky="w")
ticker_entry = ttk.Entry(frame, width=20)
ticker_entry.grid(row=0, column=1, sticky="w", padx=5)

analyze_btn = ttk.Button(frame, text="Analyze", command=analyze)
analyze_btn.grid(row=0, column=2, padx=10)

# --- Output ---
output = tk.Text(frame, wrap=tk.WORD)
output.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=10)

frame.grid_rowconfigure(1, weight=1)
frame.grid_columnconfigure(2, weight=1)

root.mainloop()