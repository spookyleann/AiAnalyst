import PySimpleGUI as sg
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

# ---------------- GUI ---------------- #

sg.theme('DarkBlue3')

layout = [
    [sg.Text('Ticker Symbol:'), sg.Input(key='-TICKER-', size=(15,1)), sg.Button('Analyze')],
    [sg.Multiline(size=(100,30), key='-OUTPUT-', autoscroll=True, disabled=True)]
]

window = sg.Window('AI Company Analyzer', layout, resizable=True, finalize=True)

def analyze(symbol):
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

        output_text = f"📊 {info.get('shortName', symbol)} ({symbol})\n"
        output_text += f"Price: ${price:.2f}\n"
        output_text += f"Market Cap: {info.get('marketCap', 'N/A')}\n\n"

        output_text += "📈 Technicals\n"
        output_text += f"SMA20: {sma:.2f}\n"
        output_text += f"RSI: {rsi:.2f}\n"
        output_text += f"Support: {support:.2f}\n"
        output_text += f"Resistance: {resistance:.2f}\n\n"

        output_text += "📉 Trend Analysis\n"
        output_text += f"Trend: {trend} ({trend_val}/100)\n"
        output_text += f"Risk Score: {risk}/100\n\n"

        output_text += "🧠 AI Investment Thesis\n"
        output_text += thesis + "\n\n"

        output_text += "📰 News\n"
        for n in news:
            output_text += f"- {n.get('title')}\n"
        output_text += f"\nSentiment Score: {sentiment}"

        # Display output
        window['-OUTPUT-'].update(output_text)

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
        window['-OUTPUT-'].update(f"Error: {e}")

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    if event == 'Analyze':
        ticker = values['-TICKER-'].upper().strip()
        if ticker:
            analyze(ticker)

window.close()