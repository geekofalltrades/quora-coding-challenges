import unittest
from search import TypeAheadSearchSession


class TestTypeAheadSearch(unittest.TestCase):
    """Test the TypeAheadSearch class."""

    def setUp(self):
        self.search = TypeAheadSearchSession()


if __name__ == '__main__':
    unittest.main()
