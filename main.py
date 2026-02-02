import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')  # Fix blank GUI issue on Mac M1
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import numpy as np
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
    scores = [TextBlob(n.get("title", "")).sentiment.polarity for n in news]
    return round(np.mean(scores), 3) if scores else 0

# ---------------- ANALYSIS ---------------- #
def trend_score(price, sma, rsi):
    score = 0
    if price > sma: score += 40
    if rsi > 55: score += 30
    if rsi > 65: score += 10
    if rsi < 45: score -= 20

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

# ---------------- GUI ---------------- #
class AIAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Company Analyzer")
        self.root.geometry("1000x700")

        # Top frame for input
        input_frame = ttk.Frame(root, padding=10)
        input_frame.pack(side='top', fill='x')

        ttk.Label(input_frame, text="Ticker Symbol:").pack(side='left')
        self.ticker_entry = ttk.Entry(input_frame, width=15)
        self.ticker_entry.pack(side='left', padx=5)
        ttk.Button(input_frame, text="Analyze", command=self.analyze).pack(side='left', padx=5)

        # Output Text
        self.output = tk.Text(root, height=15, wrap=tk.WORD)
        self.output.pack(side='top', fill='both', expand=False, padx=10, pady=5)

        # Canvas for Matplotlib chart
        self.canvas_frame = ttk.Frame(root)
        self.canvas_frame.pack(side='top', fill='both', expand=True)
        self.fig_canvas_agg = None

    def draw_figure(self, figure):
        if self.fig_canvas_agg:
            self.fig_canvas_agg.get_tk_widget().destroy()
        self.fig_canvas_agg = FigureCanvasTkAgg(figure, self.canvas_frame)
        self.fig_canvas_agg.draw()
        self.fig_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=True)

    def analyze(self):
        symbol = self.ticker_entry.get().upper().strip()
        self.output.delete("1.0", tk.END)
        if not symbol:
            self.output.insert(tk.END, "Please enter a ticker symbol.")
            return
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

            # Display text output
            output_text = f"📊 {info.get('shortName', symbol)} ({symbol})\n"
            output_text += f"Price: ${price:.2f}\nMarket Cap: {info.get('marketCap', 'N/A')}\n\n"
            output_text += f"📈 Technicals\nSMA20: {sma:.2f}\nRSI: {rsi:.2f}\nSupport: {support:.2f}\nResistance: {resistance:.2f}\n\n"
            output_text += f"📉 Trend Analysis\nTrend: {trend} ({trend_val}/100)\nRisk Score: {risk}/100\n\n"
            output_text += f"🧠 AI Investment Thesis\n{thesis}\n\n"
            output_text += "📰 News\n" + "\n".join(f"- {n.get('title')}" for n in news)
            output_text += f"\n\nSentiment Score: {sentiment}"
            self.output.insert(tk.END, output_text)

            # Draw chart
            fig, ax = plt.subplots(figsize=(10,4))
            ax.plot(df["Close"], label="Close")
            ax.plot(df["SMA20"], label="SMA20")
            ax.axhline(support, linestyle="--", alpha=0.5)
            ax.axhline(resistance, linestyle="--", alpha=0.5)
            ax.set_title(symbol)
            ax.legend()
            self.draw_figure(fig)

        except Exception as e:
            self.output.insert(tk.END, f"Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AIAnalyzer(root)
    root.mainloop()
