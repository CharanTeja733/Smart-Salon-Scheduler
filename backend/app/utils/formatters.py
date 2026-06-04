import re

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format price as currency string."""
    symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    symbol = symbols.get(currency, "$")
    return f"{symbol}{amount:.2f}"

def format_phone_display(phone: str) -> str:
    """Format +1234567890 to (123) 456-7890 (US only)."""
    if phone.startswith('+1') and len(phone) == 12:
        return f"({phone[2:5]}) {phone[5:8]}-{phone[8:12]}"
    return phone  # fallback

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def to_snake_case(name: str) -> str:
    """Convert CamelCase to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def to_camel_case(snake_str: str) -> str:
    """Convert snake_case to CamelCase."""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])