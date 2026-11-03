# Shop configuration foundation

This module is standalone and does not connect to a radio or enforce permissions yet.

Run tests from the repository root:

```sh
python3 -m unittest discover -s tests -v
```

```python
from vapor_board.config import ShopConfig, save_shop_config, load_shop_config
save_shop_config(ShopConfig(shop_name="My Shop"), "shop.json")
settings = load_shop_config("shop.json")
```

Defaults: no outbound transmissions, no MQTT, customer approval required, minimum age 21. **These settings are configuration only**; subsequent migration PRs must enforce them in every command, API, and radio entry point. No customer PII, credentials, or legacy radio configuration should be copied into settings.
