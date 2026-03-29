#!/usr/bin/env python3
"""
Trading Bot CLI — Binance Futures Testnet
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env file automatically from the project folder
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

from bot.client import BinanceAPIError, BinanceClient
from bot.logging_config import setup_logger
from bot.orders import place_limit_order, place_market_order, place_stop_market_order
from bot.validators import ValidationError

logger = setup_logger("cli")

BANNER = r"""
  ____  _                            ____        _   
 | __ )(_)_ __   __ _ _ __   ___ __|  _ \  ___ | |_ 
 |  _ \| | '_ \ / _` | '_ \ / __/ _ \ |_) |/ _ \| __|
 | |_) | | | | | (_| | | | | (_|  __/  _ <| (_) | |_ 
 |____/|_|_| |_|\__,_|_| |_|\___\___|_| \_\\___/ \__|
          Binance Futures Testnet — USDT-M
"""


def get_client() -> BinanceClient:
    """Read credentials from .env file and return a BinanceClient."""
    api_key = os.environ.get("BINANCE_API_KEY", "").strip()
    api_secret = os.environ.get("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        print("\n❌ ERROR: API credentials not found in .env file.")
        print("   Make sure your .env file exists in the project folder with:\n")
        print("   BINANCE_API_KEY=your_key_here")
        print("   BINANCE_API_SECRET=your_secret_here\n")
        sys.exit(1)

    print("✅ Loaded API credentials from .env file\n")
    return BinanceClient(api_key, api_secret)


def print_order_summary(args: argparse.Namespace) -> None:
    print("\n┌─────────────────────────────────────┐")
    print("│         ORDER REQUEST SUMMARY        │")
    print("├─────────────────────────────────────┤")
    print(f"│  Symbol     : {args.symbol:<22}│")
    print(f"│  Side       : {args.side:<22}│")
    print(f"│  Type       : {args.order_type:<22}│")
    print(f"│  Quantity   : {str(args.quantity):<22}│")
    if hasattr(args, "price") and args.price:
        print(f"│  Price      : {str(args.price):<22}│")
    if hasattr(args, "stop_price") and args.stop_price:
        print(f"│  Stop Price : {str(args.stop_price):<22}│")
    print("└─────────────────────────────────────┘\n")


def cmd_place(args: argparse.Namespace) -> None:
    print_order_summary(args)
    client = get_client()
    try:
        order_type = args.order_type.upper()
        if order_type == "MARKET":
            place_market_order(
                client=client,
                symbol=args.symbol,
                side=args.side,
                quantity=str(args.quantity),
            )
        elif order_type == "LIMIT":
            if args.price is None:
                print("❌ --price is required for LIMIT orders.")
                sys.exit(1)
            place_limit_order(
                client=client,
                symbol=args.symbol,
                side=args.side,
                quantity=str(args.quantity),
                price=str(args.price),
            )
        elif order_type == "STOP_MARKET":
            if args.stop_price is None:
                print("❌ --stop-price is required for STOP_MARKET orders.")
                sys.exit(1)
            place_stop_market_order(
                client=client,
                symbol=args.symbol,
                side=args.side,
                quantity=str(args.quantity),
                stop_price=str(args.stop_price),
            )
    except ValidationError as e:
        logger.error("Validation failed: %s", e)
        print(f"\n❌ Validation Error: {e}\n")
        sys.exit(1)
    except BinanceAPIError as e:
        logger.error("Binance API error: code=%s msg=%s", e.code, e.message)
        print(f"\n❌ Binance API Error [{e.code}]: {e.message}\n")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        print(f"\n❌ Unexpected Error: {e}\n")
        sys.exit(1)


def cmd_balance(args: argparse.Namespace) -> None:
    client = get_client()
    try:
        account = client.get_account_info()
        assets = account.get("assets", [])
        usdt = next((a for a in assets if a["asset"] == "USDT"), None)
        if usdt:
            print("\n💰 Testnet USDT Balance")
            print(f"   Wallet Balance : {usdt['walletBalance']}")
            print(f"   Available      : {usdt['availableBalance']}")
            print(f"   Unrealized PnL : {usdt['unrealizedProfit']}\n")
        else:
            print("No USDT asset found in account.\n")
    except Exception as e:
        logger.exception("Failed to fetch balance: %s", e)
        print(f"❌ Error: {e}\n")
        sys.exit(1)


def cmd_orders(args: argparse.Namespace) -> None:
    client = get_client()
    try:
        orders = client.get_open_orders(
            args.symbol if hasattr(args, "symbol") else None
        )
        if not orders:
            print("\n📋 No open orders.\n")
            return
        print(f"\n📋 Open Orders ({len(orders)} found):\n")
        for o in orders:
            print(
                f"  [{o['orderId']}] {o['symbol']} {o['side']} {o['type']} qty={o['origQty']} price={o.get('price','–')} status={o['status']}"
            )
        print()
    except Exception as e:
        logger.exception("Failed to fetch orders: %s", e)
        print(f"❌ Error: {e}\n")
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
  python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 70000
  python cli.py place --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.01 --stop-price 60000
  python cli.py balance
  python cli.py orders
        """,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_place = subparsers.add_parser("place", help="Place a new order")
    p_place.add_argument("--symbol", required=True)
    p_place.add_argument("--side", required=True, choices=["BUY", "SELL"])
    p_place.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
    )
    p_place.add_argument("--quantity", required=True, type=float)
    p_place.add_argument("--price", type=float, default=None)
    p_place.add_argument("--stop-price", dest="stop_price", type=float, default=None)
    p_place.set_defaults(func=cmd_place)

    p_balance = subparsers.add_parser("balance", help="Show account balance")
    p_balance.set_defaults(func=cmd_balance)

    p_orders = subparsers.add_parser("orders", help="List open orders")
    p_orders.add_argument("--symbol", default=None)
    p_orders.set_defaults(func=cmd_orders)

    return parser


def main() -> None:
    print(BANNER)
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
