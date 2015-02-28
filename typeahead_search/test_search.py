import unittest
from search import TypeAheadSearchSession


class TestTypeAheadSearch(unittest.TestCase):
    """Test the TypeAheadSearch class."""

    def setUp(self):
        self.search = TypeAheadSearchSession()

    def test_num_commands_int_or_int_string(self):
        """num_commands can be assigned integers or integer strings."""
        for value in (15, '15'):
            try:
                self.search.num_commands = value
            except (ValueError, TypeError):
                raise AssertionError(
                    "num_commands could not be assigned the value {}".format(
                        value
                    )
                )

    def test_num_commands_not_int(self):
        """TypeError is raised when num_commands not of type int."""
        for value in ('1.5', 'blargh', []):
            with self.assertRaises(TypeError):
                self.search.num_commands = value

    def test_num_commands_below_range(self):
        """ValueError is raised when num_commands < 0."""
        with self.assertRaises(ValueError):
            self.search.num_commands = -1

    def test_num_commands_above_range(self):
        """ValueError is raised when num_commands > 20."""
        with self.assertRaises(ValueError):
            self.search.num_commands = 21


if __name__ == '__main__':
    unittest.main()
