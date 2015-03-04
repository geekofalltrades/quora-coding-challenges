import sys
import string
from trie import TypeAheadSearchTrie


class Entry(object):
    """Simple container class for data entries."""
    def __init__(self, type, id, score, data):
        self.type = type
        self.id = id
        self.score = float(score)
        self.data = data


class TypeAheadSearchSession(object):
    """Class encapsulating a typeahead search session."""

    def __init__(self):
        self.trie = TypeAheadSearchTrie()
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
        new_entry = Entry(*command.split(None, 3))
        self.entries[new_entry.id] = new_entry

        for word in new_entry.data.lower().split():
            # Attempt to strip punctuation off of each word before storing
            # it as a search token.
            word = word.strip(string.punctuation)

            # If the word was just a blob of punctuation, don't store it.
            if not word:
                continue

            self.trie.add(word, new_entry)

    def delete(self, command):
        """Delete an item."""
        del self.entries[command]

    def query(self, command):
        """Perform a search."""
        num_results, search_words = command.split(None, 1)
        num_results = int(num_results)
        search_words = search_words.split()

        # Get the results set for one of the search words.
        results = self.trie.search(
            search_words.pop().strip(string.punctuation).lower()
        )

        # Intersect the results sets for the remaining search words into
        # the first results set.
        for word in search_words:
            results &= self.trie.search(
                word.strip(string.punctuation).lower()
            )

        return sorted(
            results,
            key=lambda e: e.score,
            reverse=True
        )[:num_results]

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
