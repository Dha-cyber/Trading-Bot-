"""
Trading Bot Dashboard — Flask Backend
Run: python app.py
Then open: http://localhost:5000
"""

import hashlib
import hmac
import os
import time
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)

BASE_URL = "https://testnet.binancefuture.com"
API_KEY = os.environ.get("BINANCE_API_KEY", "")
API_SECRET = os.environ.get("BINANCE_API_SECRET", "")


# ─────────────────────────────────────────────
# Binance helpers
# ─────────────────────────────────────────────


def _sign(params: dict) -> dict:
    params["timestamp"] = int(time.time() * 1000)
    qs = urlencode(params)
    sig = hmac.new(API_SECRET.encode(), qs.encode(), hashlib.sha256).hexdigest()
    params["signature"] = sig
    return params


def _headers():
    return {"X-MBX-APIKEY": API_KEY}


def binance_get(path: str, params: dict = {}):
    params = _sign(dict(params))
    r = requests.get(f"{BASE_URL}{path}", params=params, headers=_headers(), timeout=10)
    return r.json()


def binance_post(path: str, params: dict = {}):
    params = _sign(dict(params))
    r = requests.post(
        f"{BASE_URL}{path}", params=params, headers=_headers(), timeout=10
    )
    return r.json()


def binance_delete(path: str, params: dict = {}):
    params = _sign(dict(params))
    r = requests.delete(
        f"{BASE_URL}{path}", params=params, headers=_headers(), timeout=10
    )
    return r.json()


# ─────────────────────────────────────────────
# Routes — Pages
# ─────────────────────────────────────────────


@app.route("/")
def index():
    return render_template("index.html")


# ─────────────────────────────────────────────
# Routes — API
# ─────────────────────────────────────────────


@app.route("/api/balance")
def get_balance():
    try:
        data = binance_get("/fapi/v2/account")
        if "code" in data:
            return jsonify({"error": data.get("msg", "Unknown error")}), 400
        assets = data.get("assets", [])
        usdt = next((a for a in assets if a["asset"] == "USDT"), {})
        return jsonify(
            {
                "walletBalance": usdt.get("walletBalance", "0"),
                "availableBalance": usdt.get("availableBalance", "0"),
                "unrealizedProfit": usdt.get("unrealizedProfit", "0"),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/positions")
def get_positions():
    try:
        data = binance_get("/fapi/v2/positionRisk")
        if "code" in data:
            return jsonify({"error": data.get("msg")}), 400
        active = [p for p in data if float(p.get("positionAmt", 0)) != 0]
        return jsonify(active)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/orders")
def get_orders():
    try:
        symbol = request.args.get("symbol", "")
        params = {"symbol": symbol} if symbol else {}
        data = binance_get("/fapi/v1/openOrders", params)
        if isinstance(data, dict) and "code" in data:
            return jsonify({"error": data.get("msg")}), 400
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/order-history")
def get_order_history():
    try:
        symbol = request.args.get("symbol", "BTCUSDT")
        data = binance_get("/fapi/v1/allOrders", {"symbol": symbol, "limit": 20})
        if isinstance(data, dict) and "code" in data:
            return jsonify({"error": data.get("msg")}), 400
        return jsonify(list(reversed(data)))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/place-order", methods=["POST"])
def place_order():
    try:
        body = request.json
        params = {
            "symbol": body["symbol"].upper(),
            "side": body["side"].upper(),
            "type": body["order_type"].upper(),
            "quantity": body["quantity"],
        }
        if params["type"] == "LIMIT":
            params["price"] = body["price"]
            params["timeInForce"] = "GTC"
        elif params["type"] == "STOP_MARKET":
            params["stopPrice"] = body["stop_price"]
            params["closePosition"] = "false"

        data = binance_post("/fapi/v1/order", params)
        if "code" in data:
            return jsonify({"error": data.get("msg", "Order failed")}), 400
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cancel-order", methods=["DELETE"])
def cancel_order():
    try:
        symbol = request.args.get("symbol")
        order_id = request.args.get("orderId")
        data = binance_delete("/fapi/v1/order", {"symbol": symbol, "orderId": order_id})
        if "code" in data:
            return jsonify({"error": data.get("msg")}), 400
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/price/<symbol>")
def get_price(symbol):
    try:
        r = requests.get(
            f"{BASE_URL}/fapi/v1/ticker/price",
            params={"symbol": symbol.upper()},
            timeout=5,
        )
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("\n🤖 Trading Bot Dashboard")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ Open in browser: http://localhost:5000")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    app.run(debug=True, port=5000)
