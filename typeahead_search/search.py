import sys
from warnings import warn


class TypeAheadSearchSession(object):
    """Class encapsulating a typeahead search session."""

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

        if value < 0 or value > 20:
            raise ValueError(
                "num_commands must be between 0 and 20, inclusive."
            )

        self._num_commands = value

    def __init__(self, num_commands=0):
        self.num_commands = num_commands

        # Keep a record of all commands processed.
        self.commands = []

    def run_command(self, command):
        """Validate and execute a search command."""
        # Store this command in the list of commands we have attempted
        # to execute.
        self.commands.append(command)

        if command.startswith('ADD '):
            self.add(command[4:])
        elif command.startswith('DEL '):
            self.delete(command[4:])
        elif command.startswith('QUERY '):
            self.query(command[6:])
        elif command.startswith('WQUERY '):
            self.wquery(command[7:])
        else:
            raise ValueError(
                "Command \"{}\" is not of type ADD, DEL, QUERY,"
                " or WQUERY.".format(command)
            )


class InputWarning(UserWarning):
    """Warning raised when input is longer or shorter than expected."""


def main(session=None):
    """Main search loop."""
    if not session:
        session = TypeAheadSearchSession()

    # Get the number of expected commands.
    try:
        session.num_commands = sys.stdin.readline().strip()

    except (ValueError, TypeError) as e:
        # Raise a new exception with a more elucidating error message.
        raise type(e)(e.args[0].replace('num_commands', "First line of input"))

    # Fetch each command from the input.
    for i in range(session.num_commands):
        command = sys.stdin.readline().strip()

        # If no input is available, raise a warning and break from this loop.
        if not command:
            warn(
                "Ecountered unexpected EOF. (Did you provide fewer"
                " than {} commands?)".format(session.num_commands),
                InputWarning
            )
            break

        session.run_command(command)

    # Check whether any input remains, and warn, if so.
    command = sys.stdin.readline().strip()
    if command:
        warn(
            "Encountered unexpected input. (Did you provide more"
            " than {} commands?) Lines from \"{}\" will not be"
            " evaluated.".format(session.num_commands, command),
            InputWarning
        )


if __name__ == '__main__':
    main()
