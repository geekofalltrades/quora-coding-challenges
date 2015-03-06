import sys
import string


class TypeAheadSearchTrie(object):
    """A Trie (prefix tree) class for use in typeahead search.

    Every node in the TypeAheadSearchTrie is another TypeAheadSearchTrie
    instance.
    """
    def __init__(self):
        # The children of this node. Because ordered traversals are not
        # important, these are stored in a dictionary.
        self.children = {}

        # Data entries associated with the prefix stored in the path to
        # this node.
        self.entries = set()

    def __contains__(self, word):
        if word:
            try:
                return self.children[word[0]].__contains__(word[1:])
            except KeyError:
                return False

        else:
            return any(
                self.entries - child.entries
                for child in self.children.values()
            )

    def add(self, word, entry):
        """Adds the given data entry to the given Trie word.
        The word is created in the Trie if it doesn't already exist.
        """
        self.entries.add(entry)
        if word:
            self.children.setdefault(
                word[0],
                TypeAheadSearchTrie()
            ).add(word[1:], entry)

    def delete(self, word, entry):
        """Deletes the given data entry from the given Trie word.
        The word is removed if it becomes empty.
        """
        self.entries.discard(entry)
        if not self.entries:
            return True
        elif word:
            if self.children[word[0]].delete(word[1:], entry):
                del self.children[word[0]]

        return False

    def search(self, word):
        """Return a set of all data entries represented by prefix `word`.
        Returns an empty set if this prefix is not in the Trie.
        """
        if word:
            try:
                return self.children[word[0]].search(word[1:])
            except KeyError:
                return set()

        else:
            return self.entries

    def gather_entries(self):
        """Gather all data entries stored in this node and its children."""
        entries = set(self.entries)
        for child in self.children.itervalues():
            entries.update(child.gather_entries())
        return entries


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
            return self.query(command[6:])
        elif command.startswith('WQUERY '):
            return self.wquery(command[7:])
        else:
            raise ValueError(
                "Command \"{}\" is not of type ADD, DEL, QUERY,"
                " or WQUERY.".format(command)
            )

    def add(self, command):
        """Add a new item."""
        type, id, score, data = command.split(None, 3)
        new_entry = (type, id, float(score), data)
        self.entries[id] = new_entry

        for word in data.lower().split():
            # Attempt to strip punctuation off of each word before storing
            # it as a search token.
            word = word.strip(string.punctuation)

            # If the word was just a blob of punctuation, don't store it.
            if not word:
                continue

            self.trie.add(word, new_entry)

    def delete(self, command):
        """Delete an item."""
        for word in self.entries[command][3].lower().split():
            word = word.strip(string.punctuation)
            if not word:
                continue

            self.trie.delete(word, self.entries[command])

        del self.entries[command]

    def _query_base(self, *search_words):
        """The portion of prefix search common to both query and wquery."""
        # Get the results set for one of the search words.
        results = self.trie.search(
            search_words[0].strip(string.punctuation).lower()
        )

        # Intersect the results sets for the remaining search words into
        # the first results set.
        for word in search_words[1:]:
            results &= self.trie.search(
                word.strip(string.punctuation).lower()
            )

        return results

    def query(self, command):
        """Perform a search."""
        num_results, search_words = command.split(None, 1)
        num_results = int(num_results)

        return sorted(
            self._query_base(*search_words.split()),
            key=lambda e: e.score,
            reverse=True
        )[:num_results]

    def wquery(self, command):
        """Perform a weighted search."""
        num_results, num_boosts, search_words = command.split(None, 2)
        num_results, num_boosts = int(num_results), int(num_boosts)

        boosts = {}
        for i in range(num_boosts):
            boost, search_words = search_words.split(None, 1)
            key, value = boost.split(':')
            if key in boosts:
                boosts[key] *= float(value)
            else:
                boosts[key] = float(value)

        return sorted(
            self._query_base(*search_words.split()),
            key=lambda e: e.score * boosts.get(e.type, 1) * boosts.get(e.id, 1),
            reverse=True
        )[:num_results]


def main(session=None):
    """Main search loop."""
    if not session:
        session = TypeAheadSearchSession()

    # Get the number of expected commands.
    num_commands = int(sys.stdin.readline().strip())

    # Fetch each command from the input.
    for i in range(num_commands):
        command = sys.stdin.readline().strip()
        results = session.run_command(command)
        if results is not None:
            print ' '.join(result.id for result in results)


if __name__ == '__main__':
    main()
