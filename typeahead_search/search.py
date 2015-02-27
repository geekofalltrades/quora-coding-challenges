import sys
from warnings import warn


class TypeAheadSearch(object):
    """Class encapsulating the action of the typeahead search."""

    def __init__(self):
        # Keep a record of all commands processed.
        self.commands = []

    def main(self):
        """Main search loop."""
        # Get the number of expected commands.
        self.num_commands = self.get_num_commands()

        # Fetch each command from the input.
        for i in range(self.num_commands):
            try:
                self.parse_command()

            except InputWarning as e:
                # warn with the InputWarning and terminate this loop.
                warn(e.message, e.__class__, stacklevel=2)
                break

        # Check whether any input remains, and warn, if so.
        command = sys.stdin.readline().strip()
        if command:
            warn(
                "Encountered unexpected input. (Did you provide more"
                " than {} commands?) Lines from \"{}\" will not be"
                " evaluated.".format(self.num_commands, command),
                InputWarning
            )

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

    def parse_command(self):
        """Read, validate, and execute a command from stdin."""
        command = sys.stdin.readline().strip()

        # If no input is available, raise a warning.
        if not command:
            raise InputWarning(
                "Ecountered unexpected EOF. (Did you provide fewer"
                " than {} commands?)".format(self.num_commands)
            )

        # Otherwise, store this command in the list of commands we have
        # attempted to execute.
        self.commands.append(command)

        # Begin parsing this command.


class InputWarning(UserWarning):
    """Warning raised when input is longer or shorter than expected."""


if __name__ == '__main__':
    search = TypeAheadSearch()
    search.main()
