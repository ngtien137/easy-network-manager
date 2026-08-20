import os
import sys
import unittest

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.process_scanner import WindowsProcessScanner
from core.models import ProcessCategory


class TestProcessScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = WindowsProcessScanner()

    def test_scan_all_returns_processes(self):
        processes = self.scanner.scan_all(blocked_paths=set())
        self.assertGreater(len(processes), 0, "Process list should not be empty")

        # Check that we have both Apps or Background processes
        categories = {p.category for p in processes}
        self.assertTrue(ProcessCategory.BACKGROUND in categories or ProcessCategory.APP in categories)

    def test_system_summary(self):
        processes = self.scanner.scan_all(blocked_paths=set())
        summary = self.scanner.get_system_summary(processes)
        self.assertGreaterEqual(summary.total_cpu_percent, 0.0)
        self.assertGreater(summary.total_memory_gb, 0.0)
        self.assertGreater(summary.total_background_count + summary.total_apps_count, 0)


if __name__ == "__main__":
    unittest.main()
