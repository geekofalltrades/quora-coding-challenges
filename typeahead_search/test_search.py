import unittest


class TestTypeAheadSearch(unittest.TestCase):
    """Test the TypeAheadSearch class."""

    def test_num_commands_int_or_int_string(self):
        """num_commands can be assigned integers or integer strings."""

    def test_num_commands_not_int(self):
        """TypeError is raised when num_commands not of type int."""

    def test_num_commands_below_range(self):
        """ValueError is raised when num_commands < 0."""

    def test_num_commands_above_range(self):
        """ValueError is raised when num_commands > 20."""


if __name__ == '__main__':
    unittest.main()
