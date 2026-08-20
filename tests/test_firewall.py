import os
import sys
import unittest

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.firewall_service import WindowsFirewallService


class TestFirewallService(unittest.TestCase):
    def setUp(self):
        self.service = WindowsFirewallService()

    def test_normalize_path(self):
        p1 = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        p2 = r"c:/program files/google/chrome/application/chrome.exe"
        self.assertEqual(
            self.service._normalize_path(p1),
            self.service._normalize_path(p2)
        )

    def test_rule_id_generation(self):
        rule_id = self.service._generate_rule_id("chrome.exe", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        self.assertTrue(rule_id.startswith(WindowsFirewallService.RULE_PREFIX))
        self.assertIn("chrome", rule_id.lower())


if __name__ == "__main__":
    unittest.main()
