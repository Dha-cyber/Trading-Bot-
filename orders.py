"""High-level order placement logic — sits between client and CLI."""

from bot.client import BinanceClient
from bot.logging_config import setup_logger
from bot.validators import validate_order_inputs

logger = setup_logger("orders")


def _format_order_response(data: dict) -> str:
    """Return a human-readable order summary string."""
    lines = [
        "",
        "╔══════════════════════════════════════════════════╗",
        "║              ORDER RESPONSE SUMMARY              ║",
        "╚══════════════════════════════════════════════════╝",
        f"  Order ID      : {data.get('orderId', 'N/A')}",
        f"  Client OID    : {data.get('clientOrderId', 'N/A')}",
        f"  Symbol        : {data.get('symbol', 'N/A')}",
        f"  Side          : {data.get('side', 'N/A')}",
        f"  Type          : {data.get('type', 'N/A')}",
        f"  Status        : {data.get('status', 'N/A')}",
        f"  Orig Qty      : {data.get('origQty', 'N/A')}",
        f"  Executed Qty  : {data.get('executedQty', 'N/A')}",
        f"  Avg Price     : {data.get('avgPrice', data.get('price', 'N/A'))}",
        f"  Time in Force : {data.get('timeInForce', 'N/A')}",
        f"  Created At    : {data.get('updateTime', 'N/A')} (ms epoch)",
        "──────────────────────────────────────────────────",
    ]
    return "\n".join(lines)


def place_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: str,
) -> dict:
    """Place a MARKET order."""
    validated = validate_order_inputs(
        symbol=symbol,
        side=side,
        order_type="MARKET",
        quantity=quantity,
    )

    logger.info(
        "Market order request | symbol=%s side=%s qty=%s",
        validated["symbol"],
        validated["side"],
        validated["quantity"],
    )

    result = client.place_order(
        symbol=validated["symbol"],
        side=validated["side"],
        type="MARKET",
        quantity=validated["quantity"],
    )

    print(_format_order_response(result))
    print(f"  ✅ MARKET order placed successfully!\n")
    logger.info(
        "Market order placed | orderId=%s status=%s",
        result.get("orderId"),
        result.get("status"),
    )
    return result


def place_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: str,
    price: str,
) -> dict:
    """Place a LIMIT order (GTC by default)."""
    validated = validate_order_inputs(
        symbol=symbol,
        side=side,
        order_type="LIMIT",
        quantity=quantity,
        price=price,
    )

    logger.info(
        "Limit order request | symbol=%s side=%s qty=%s price=%s",
        validated["symbol"],
        validated["side"],
        validated["quantity"],
        validated["price"],
    )

    result = client.place_order(
        symbol=validated["symbol"],
        side=validated["side"],
        type="LIMIT",
        quantity=validated["quantity"],
        price=validated["price"],
        timeInForce="GTC",
    )

    print(_format_order_response(result))
    print(f"  ✅ LIMIT order placed successfully!\n")
    logger.info(
        "Limit order placed | orderId=%s status=%s",
        result.get("orderId"),
        result.get("status"),
    )
    return result


def place_stop_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: str,
    stop_price: str,
) -> dict:
    """Place a STOP_MARKET order (bonus order type)."""
    validated = validate_order_inputs(
        symbol=symbol,
        side=side,
        order_type="STOP_MARKET",
        quantity=quantity,
        stop_price=stop_price,
    )

    logger.info(
        "Stop-market order request | symbol=%s side=%s qty=%s stopPrice=%s",
        validated["symbol"],
        validated["side"],
        validated["quantity"],
        validated["stop_price"],
    )

    result = client.place_order(
        symbol=validated["symbol"],
        side=validated["side"],
        type="STOP_MARKET",
        quantity=validated["quantity"],
        stopPrice=validated["stop_price"],
        closePosition="false",
    )

    print(_format_order_response(result))
    print(f"  ✅ STOP_MARKET order placed successfully!\n")
    logger.info(
        "Stop-market order placed | orderId=%s status=%s",
        result.get("orderId"),
        result.get("status"),
    )
    return result
