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
            pass

    def get_num_commands(self):
        """Read the number of expected commands from stdin."""

    def parse_command(self, command):
        """Parse and validate individual commands."""


if __name__ == '__main__':
    search = TypeAheadSearch()
    search.main()
