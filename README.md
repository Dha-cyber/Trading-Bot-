# Trading-Bot-
Binance Futures Testnet Trading Bot
# 🤖 Trading Bot — Binance Futures Testnet (USDT-M)

A Python CLI trading bot and web dashboard for placing and managing orders on the Binance Futures Testnet. Built with clean, modular architecture, structured logging, and full error handling.

---

## 📁 Project Structure

```
trading_bot/
├── app.py                  # Flask web dashboard (bonus UI)
├── cli.py                  # CLI entry point
├── .env                    # API credentials (not committed to git)
├── requirements.txt
├── README.md
├── templates/
│   └── index.html          # Dashboard frontend
├── bot/
│   ├── __init__.py
│   ├── client.py           # Binance Futures REST API wrapper
│   ├── orders.py           # Order placement logic (market, limit, stop)
│   ├── validators.py       # Input validation
│   └── logging_config.py  # Logging setup (file + console)
└── logs/
    ├── trading_bot_20260329.log 
    
```

---

## ⚙️ Setup Steps

### 1. Get Binance Futures Testnet API Keys

1. Go to **https://testnet.binancefuture.com** (separate from main Binance — no KYC needed)
2. Register with just email + password
3. Log in → scroll down on the trading page → click **"API Key"** tab
4. Generate and copy your **API Key** and **Secret Key**

### 2. Clone / Download the Project

```bash
git clone https://github.com/YOUR_USERNAME/trading-bot.git
cd trading-bot
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the project root:

```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

## 🚀 How to Run — CLI

### Check account balance
```bash
python cli.py balance
```

### Place a MARKET BUY order
```bash
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Place a MARKET SELL order
```bash
python cli.py place --symbol ETHUSDT --side SELL --type MARKET --quantity 0.1
```

### Place a LIMIT BUY order
```bash
python cli.py place --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01 --price 60000
```

### Place a LIMIT SELL order
```bash
python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 70000
```

### Place a STOP_MARKET order *(bonus order type)*
```bash
python cli.py place --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.01 --stop-price 60000
```

### List all open orders
```bash
python cli.py orders
python cli.py orders --symbol BTCUSDT
```

### Get help
```bash
python cli.py --help
python cli.py place --help
```

---

## 🖥️ How to Run — Web Dashboard *(bonus feature)*

```bash
python app.py
```

Then open your browser and go to: **http://localhost:5000**

The dashboard provides:
- Live wallet balance, available balance, unrealized PnL
- Place MARKET / LIMIT / STOP orders from the UI
- View and cancel open orders
- View active positions with entry price and PnL
- Order history (last 20 orders per symbol)
- Live BTC/ETH price tickers (auto-refresh every 5 seconds)

---

## 📝 Logging

Logs are automatically saved to the `logs/` directory.

- **Filename format:** `trading_bot_YYYYMMDD.log`
- **Console:** shows INFO level and above
- **Log file:** captures full DEBUG detail including raw API request/response

**Example log entry (MARKET order):**
```
2025-01-15 10:22:01 | INFO     | orders | Market order request | symbol=BTCUSDT side=BUY qty=0.01
2025-01-15 10:22:01 | INFO     | binance_client | Order placed successfully. ID: 3841923
2025-01-15 10:22:01 | INFO     | orders | Market order placed | orderId=3841923 status=FILLED
```

---

## 🧩 Architecture

| Layer | File | Responsibility |
|-------|------|----------------|
| CLI | `cli.py` | Argument parsing, user-facing output |
| API Client | `bot/client.py` | HMAC signing, HTTP requests, error handling |
| Order Logic | `bot/orders.py` | Business logic for each order type |
| Validation | `bot/validators.py` | Input sanitization before any API call |
| Logging | `bot/logging_config.py` | Dual-output logger (console + file) |
| Dashboard | `app.py` + `templates/` | Flask web UI (bonus) |


---

## 📌 Assumptions

- Only **USDT-M Futures Testnet** is supported (not Spot or COIN-M)
- `timeInForce` for LIMIT orders defaults to **GTC** (Good Till Cancelled)
- API credentials are stored in a `.env` file (not environment variables or hardcoded)
- Python **3.10+** is required
- The web dashboard (`app.py`) is a bonus feature — the core bot runs fully via `cli.py`
- Quantity precision depends on the symbol (e.g. BTCUSDT min is 0.001)

---

## 📦 Dependencies

```
requests>=2.31.0
python-dotenv>=1.0.0
flask>=3.0.0
```

Install all with:
```bash
pip install -r requirements.txt
```

---

Thankyou!!
