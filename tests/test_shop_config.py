import json
import tempfile
import unittest
from pathlib import Path

from vapor_board.config import ShopConfig, load_shop_config, save_shop_config


class ShopConfigTests(unittest.TestCase):
    def test_safe_defaults(self):
        config = ShopConfig()
        self.assertFalse(config.transmissions_enabled)
        self.assertFalse(config.mqtt_enabled)
        self.assertTrue(config.customer_access_requires_approval)
        self.assertEqual(config.minimum_customer_age, 21)

    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "shop.json"
            original = ShopConfig(shop_name="Example Shop", accent_color="#112233")
            save_shop_config(original, path)
            self.assertEqual(load_shop_config(path), original)

    def test_missing_file_is_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(load_shop_config(Path(directory) / "missing.json"), ShopConfig())

    def test_invalid_settings_rejected(self):
        for kwargs in ({"shop_name": ""}, {"accent_color": "blue"},
                       {"minimum_customer_age": 18}, {"transmissions_enabled": "false"}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    ShopConfig(**kwargs)

    def test_unknown_settings_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "shop.json"
            path.write_text(json.dumps({"radio_password": "secret"}))
            with self.assertRaises(ValueError):
                load_shop_config(path)


if __name__ == "__main__":
    unittest.main()
