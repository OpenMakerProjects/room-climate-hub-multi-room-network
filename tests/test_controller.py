import math
import unittest

from src.main import Controller


class ControllerTests(unittest.TestCase):
    def test_rejects_invalid_reading(self):
        controller = Controller(confirmations=1)
        snapshot = controller.evaluate([math.nan])
        self.assertFalse(snapshot.valid)
        self.assertFalse(controller.output_active)

    def test_requires_confirmations(self):
        controller = Controller(threshold=0.5, confirmations=2)
        controller.evaluate([0.9, 0.9])
        self.assertFalse(controller.output_active)
        controller.evaluate([0.9, 0.9])
        self.assertTrue(controller.output_active)

    def test_low_reading_resets_output(self):
        controller = Controller(threshold=0.5, confirmations=1)
        controller.evaluate([0.9])
        self.assertTrue(controller.output_active)
        controller.evaluate([0.1])
        self.assertFalse(controller.output_active)


if __name__ == "__main__":
    unittest.main()
