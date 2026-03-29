"""Validation helpers for CLI inputs."""

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


class ValidationError(ValueError):
    """Raised when user input fails validation."""


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s or not s.isalpha():
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Must be letters only (e.g. BTCUSDT)."
        )
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}."
        )
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}."
        )
    return t


def validate_quantity(quantity: str) -> float:
    try:
        q = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(
            f"Invalid quantity '{quantity}'. Must be a positive number."
        )
    if q <= 0:
        raise ValidationError(f"Quantity must be greater than 0. Got: {q}")
    return q


def validate_price(price: str) -> float:
    try:
        p = float(price)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid price '{price}'. Must be a positive number.")
    if p <= 0:
        raise ValidationError(f"Price must be greater than 0. Got: {p}")
    return p


def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
    stop_price: str | None = None,
) -> dict:
    """Validate all order inputs and return a cleaned dict."""
    cleaned = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
    }

    if cleaned["order_type"] == "LIMIT":
        if price is None:
            raise ValidationError("Price is required for LIMIT orders.")
        cleaned["price"] = validate_price(price)

    if cleaned["order_type"] == "STOP_MARKET":
        if stop_price is None:
            raise ValidationError("Stop price is required for STOP_MARKET orders.")
        cleaned["stop_price"] = validate_price(stop_price)

    return cleaned
