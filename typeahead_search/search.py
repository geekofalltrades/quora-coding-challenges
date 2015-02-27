import sys
from warnings import warn


class TypeAheadSearch(object):
    """Class encapsulating the action of the typeahead search."""

    @property
    def num_commands(self):
        return self._num_commands

    @num_commands.setter
    def num_commands(self, value):
        try:
            value = int(value)
        except ValueError:
            raise TypeError(
                "num_commands must be an integer or integer string literal."
            )

        if value <= 0 or value > 20:
            raise ValueError(
                "num_commands must be between 1 and 20, inclusive."
            )

        self._num_commands = value

    def __init__(self):
        # Keep a record of all commands processed.
        self.commands = []

    def main(self):
        """Main search loop."""
        # Get the number of expected commands.
        self.num_commands = self.get_num_commands(
            sys.stdin.readline().strip()
        )

        # Fetch each command from the input.
        for i in range(self.num_commands):
            command = sys.stdin.readline().strip()

            # If no input is available, raise a warning.
            if not command:
                warn(
                    "Ecountered unexpected EOF. (Did you provide fewer"
                    " than {} commands?)".format(self.num_commands),
                    InputWarning
                )

            self.parse_command(command)

        # Check whether any input remains, and warn, if so.
        command = sys.stdin.readline().strip()
        if command:
            warn(
                "Encountered unexpected input. (Did you provide more"
                " than {} commands?) Lines from \"{}\" will not be"
                " evaluated.".format(self.num_commands, command),
                InputWarning
            )

    def parse_command(self, command):
        """Read, validate, and execute a command from stdin."""
        # Store this command in the list of commands we have attempted
        # to execute.
        self.commands.append(command)

        # Begin parsing this command.


class InputWarning(UserWarning):
    """Warning raised when input is longer or shorter than expected."""


if __name__ == '__main__':
    search = TypeAheadSearch()
    search.main()
