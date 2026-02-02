# AiAnalyst

# AI Company Analyzer

An AI-powered Python application that analyzes publicly traded companies using:
- Market data
- Technical indicators
- Financial fundamentals
- News sentiment analysis

Users can input any investable ticker symbol (IPO or public company) and receive a structured analysis.

---

## Features
- Stock price & financials (Yahoo Finance)
- Technical indicators (RSI, SMA)
- News scraping & sentiment analysis
- Standalone Python GUI (Tkinter)
- macOS / Windows compatible
- No admin privileges required

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/ai-company-analyzer.git
cd ai-company-analyzer
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python ai_stock_analyzer.py