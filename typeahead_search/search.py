import sys
import string
from operator import itemgetter


class TypeAheadRadixTrie(object):
    """A Radix Trie class for use in typeahead search."""

    def __init__(self, entries=None):
        """Create a new TypeAheadRadixTrie.
        If entries is a set, copy it to self.entries."""

        # The children of this node. Because ordered traversals are not
        # important, these are stored in a dictionary.
        self.children = {}

        # Data entry ids associated with the prefix stored in the path to
        # this node.
        if entries:
            self.entries = entries.copy()
        else:
            self.entries = set()

    def __contains__(self, word):
        """Determines whether words (not entries) are stored in the Trie.
        For use in testing.
        """
        if word:
            for path in self.children:
                if word.startswith(path):
                    return self.children[path].__contains__(word[len(path):])
            else:
                return False
        else:
            return True

    def add(self, word, id):
        """Adds the given data entry id to the given Radix Trie word.
        The word is created in the Radix Trie if it doesn't already exist.
        """
        self.entries.add(id)

        if word:
            prefixes = tuple(word[:i] for i in range(len(word), 0, -1))

            # Check whether we have a path that prefixes our word.
            for prefix in prefixes:
                # If we have a path that prefixes our word, follow it.
                if prefix in self.children:
                    self.children[prefix].add(word[len(prefix):], id)
                    return

            # Check whether prefixes of our word prefix an existing path.
            for path in self.children:
                for prefix in prefixes:
                    # If this prefix prefixes an existing path, split the
                    # path in two and insert a new node accommodating this
                    # word.
                    if path.startswith(prefix):
                        self.children[prefix] = TypeAheadRadixTrie(
                            self.children[path].entries
                        )
                        self.children[prefix].children[path[len(prefix):]] = \
                            self.children[path]

                        del self.children[path]
                        self.children[prefix].add(word[len(prefix):], id)
                        return

            # If we have no paths prefixing or prefixed by this word, create
            # a new path representing this word.
            self.children[word] = TypeAheadRadixTrie()
            self.children[word].add('', id)

    def delete(self, word, id):
        """Deletes the given data entry id from the given Radix Trie word.
        The word is removed if it becomes empty.
        """
        # Discard the entry, if it hasn't already been discarded.
        self.entries.discard(id)

        # If we have no entries left, return True, signalling to our
        # caller that we should be deleted.
        if not self.entries:
            return True

        # If we still have entries and there's still postfix left to search,
        # pass on the remaining postfix to the appropriate child node, if any.
        # Delete the child node if it tells us it's empty.
        elif word:
            for path in self.children:
                if word.startswith(path):
                    if self.children[path].delete(word[len(path):], id):
                        del self.children[path]
                    break

        return False

    def search(self, word):
        """Return a set of all data entry ids represented by prefix `word`.
        Returns an empty set if this prefix is not in the Trie.
        """
        if word:
            # Check whether a path prefixes our word.
            for prefix, postfix in (
                (word[:i], word[i:]) for i in range(len(word), 0, -1)
            ):
                if prefix in self.children:
                    return self.children[prefix].search(postfix)

            # Check whether our word prefixes a path.
            for path in self.children:
                if path.startswith(word):
                    return self.children[path].search('')

            return set()

        else:
            return self.entries


class TypeAheadSearchSession(object):
    """Class encapsulating a typeahead search session."""

    def __init__(self):
        self.trie = TypeAheadRadixTrie()
        self.entries = {}
        self.added = 0

    def run_command(self, command):
        """Validate and execute a search command."""
        command_type, command = command.split(None, 1)
        if command_type == 'ADD':
            self.add(command)
        elif command_type == 'DEL':
            self.delete(command)
        elif command_type == 'QUERY':
            return self.query(command)
        elif command_type == 'WQUERY':
            return self.wquery(command)
        else:
            raise ValueError(
                "Command \"{}\" is not of type ADD, DEL, QUERY,"
                " or WQUERY.".format(command)
            )

    def add(self, command):
        """Add a new item."""
        type, id, score, data = command.split(None, 3)
        self.added += 1
        new_entry = (type, id, float(score), data, self.added)
        self.entries[id] = new_entry

        for word in data.lower().split():
            # Attempt to strip punctuation off of each word before storing
            # it as a search token.
            word = word.strip(string.punctuation)

            # If the word was just a blob of punctuation, don't store it.
            if not word:
                continue

            self.trie.add(word, id)

    def delete(self, id):
        """Delete an item."""
        for word in self.entries[id][3].lower().split():
            word = word.strip(string.punctuation)
            if not word:
                continue

            # If the Trie signals that it no longer holds any entries,
            # allocate a new Trie. This is an edge case that otherwise
            # leaves behind residual entries in the case where the Trie
            # only holds one record, and it allows us to short-circuit
            # the rest of our deletions.
            if self.trie.delete(word, id):
                self.trie = TypeAheadRadixTrie()
                break

        del self.entries[id]

    def _query_base(self, *search_words):
        """The portion of prefix search common to both query and wquery."""
        # Get the results set for one of the search words.
        results = self.trie.search(
            search_words[0].strip(string.punctuation).lower()
        ).copy()

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
            (self.entries[id] for id in self._query_base(*search_words.split())),
            key=itemgetter(2, 4),
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
            (self.entries[id] for id in self._query_base(*search_words.split())),
            key=lambda e: (
                e[2] * boosts.get(e[0], 1) * boosts.get(e[1], 1),
                e[4]
            ),
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
            print ' '.join(result[1] for result in results)


if __name__ == '__main__':
    main()
