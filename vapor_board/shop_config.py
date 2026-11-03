"""Single-shop identity configuration, with no credentials or customer records."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ShopConfig:
    name: str
    city: str = ""
    contact: str = ""
    accent: str = "#17BEBB"


def validate_shop_config(config: ShopConfig) -> ShopConfig:
    if not isinstance(config.name, str) or not 1 <= len(config.name.strip()) <= 100:
        raise ValueError("Shop name must be 1-100 characters")
    if any(ord(c) < 32 for c in config.name):
        raise ValueError("Shop name contains control characters")
    if not isinstance(config.accent, str) or len(config.accent) != 7 or config.accent[0] != '#' or any(c not in '0123456789abcdefABCDEF' for c in config.accent[1:]):
        raise ValueError("Accent must be a six-digit hex color")
    return config
