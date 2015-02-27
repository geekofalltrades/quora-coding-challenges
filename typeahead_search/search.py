import sys


class TypeAheadSearch(object):
    """Class encapsulating the action of the typeahead search."""

    def __init__(self):
        # Keep a record of all commands processed.
        self.commands = []

    def main(self):
        """Main search loop."""
        # Get the number of expected commands.
        self.num_commands = self.get_num_commands()

        # Loop through individual commands.
        for i in range(self.num_commands):
            command = sys.stdin.readline().strip()
            if not command:
                raise ValueError

    def get_num_commands(self):
        """Read the number of expected commands from stdin."""
        try:
            num_commands = int(sys.stdin.readline().strip())
        except ValueError:
            raise TypeError(
                "First line of input must be an integer."
            )

        if num_commands <= 0 or num_commands > 20:
            raise ValueError(
                "First line of input must be between 1 and 20, inclusive."
            )

    def parse_command(self, command):
        """Parse and validate individual commands."""


if __name__ == '__main__':
    search = TypeAheadSearch()
    search.main()
