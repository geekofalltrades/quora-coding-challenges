import sys
from trie import TypeaheadSearchTrie


class Entry(object):
    """Simple container class for data entries."""
    def __init__(self, type, id, score, data):
        self.type = type
        self.id = id
        self.score = score
        self.data = data


class TypeAheadSearchSession(object):
    """Class encapsulating a typeahead search session."""

    def __init__(self):
        self.trie = TypeaheadSearchTrie()
        self.entries = {}

    def run_command(self, command):
        """Validate and execute a search command."""
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

    def add(self, command):
        """Add a new item."""
        new_entry = Entry(*command.split(maxsplit=3))
        self.entries[new_entry.id] = new_entry

        for word in new_entry.data.lower().split():
            self.trie.add(word, new_entry)

    def delete(self, command):
        """Delete an item."""

    def query(self, command):
        """Perform a search."""

    def wquery(self, command):
        """Perform a weighted search."""


def main(session=None):
    """Main search loop."""
    if not session:
        session = TypeAheadSearchSession()

    # Get the number of expected commands.
    num_commands = sys.stdin.readline().strip()

    # Fetch each command from the input.
    for i in range(num_commands):
        command = sys.stdin.readline().strip()
        session.run_command(command)


if __name__ == '__main__':
    main()
