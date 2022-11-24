import unittest
from main import getIndex
import numpy


class TestGetIndex(unittest.TestCase):
    def test(self):
        self.assertEqual(getIndex(numpy.array([0, 1, 0, 1, 0, 1]), 2, (3, 5)), 39)
        self.assertEqual(
            getIndex(numpy.array([0, 1, 2, 0, 1, 2, 0, 1, 2]), 3, (4, 3, 5)), 342
        )
        self.assertEqual(
            getIndex(numpy.array([2, 2, 0, 1, 1, 2, 0, 1, 0]), 3, (4, 3, 5)), 313
        )


if __name__ == "__main__":
    unittest.main()
