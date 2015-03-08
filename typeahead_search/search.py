import sys
import string
from operator import itemgetter
from os.path import commonprefix


class TypeAheadRadixTrie(object):
    """A Radix Trie class for use in typeahead search."""

    def __init__(self, entries=None, root=True):
        """Create a new TypeAheadRadixTrie.
        If entries is a set, copy it to self.entries.
        If root is True, we are the root node.
        """

        # The children of this node. Because ordered traversals are not
        # important, these are stored in a dictionary.
        # Each path is keyed with its first letter, and stores a tuple
        # of (path, child).
        self.children = {}

        # Whether or not this is the root node.
        self.root = root

        # Data entry ids associated with the prefix stored in the path to
        # this node.
        if not self.root and entries:
            self.entries = entries.copy()
        else:
            self.entries = set()

    def __contains__(self, word):
        """Determines whether words (not entries) are stored in the Radix Trie.
        For use in testing.
        """
        if word:
            path, child = self.children.get(word[0], ('', None))
            if path and word.startswith(path):
                    return child.__contains__(word[len(path):])
            else:
                return False
        else:
            return True

    def __nonzero__(self):
        """Return true if this node contains entries, False otherwise.
        The root always evaluates to True.
        """
        return self.root or bool(self.entries)

    def add(self, word, id):
        """Adds the given data entry id to the given Radix Trie word.
        The word is created in the Radix Trie if it doesn't already exist.
        """
        # Don't store entries if we are the root.
        if not self.root:
            self.entries.add(id)

        if word:
            # Retrieve the candidate path, or create a path for this
            # word if a candidate path doesn't exist.
            path, child = self.children.setdefault(
                word[0],
                (word, TypeAheadRadixTrie(root=False))
            )

            # Get the longest prefix the path and the word share.
            common = commonprefix((word, path))

            # If the path prefixes the word, pass on the postfix to the child.
            if common == path:
                child.add(word[len(path):], id)

            # If the word and the path share a prefix, split the path in
            # two and insert a new node, then add the remainder of this
            # word from that node.
            else:
                new_child = TypeAheadRadixTrie(child.entries, root=False)
                new_child_path = path[len(common):]
                self.children[word[0]] = (common, new_child)
                new_child.children[new_child_path[0]] = (
                    new_child_path,
                    child
                )
                new_child.add(word[len(common):], id)

    def delete(self, word, id):
        """Deletes the given data entry id from the given Radix Trie word.
        Postfixes are removed if they become empty.
        Nodes are collapsed if deletion causes them to represent a single path.
        """
        # Discard the entry, if it hasn't already been discarded.
        self.entries.discard(id)

        # If we have no entries left, and we are not the root, short-circuit.
        # Our parent will delete us.
        if not self.root and not self.entries:
            return

        # If we have postfix left to search.
        if word:
            # Get the path to the remaining postfix of the word, if any.
            path, child = self.children.get(word[0], ('', None))

            # If we have a path prefixing this word, follow it.
            if path and word.startswith(path):
                new_path = child.delete(word[len(path):], id)

                # If our child returned a path that it collapsed into
                # itself, update our path to that child with the returned
                # path.
                if new_path:
                    self.children[word[0]] = (path + new_path, child)

                # If the node at the end of this path contains no more
                # entries, delete it.
                elif not child:
                    del self.children[word[0]]

        # If only one child now remains, and our set of entries is equal
        # to that child's set of entries (never true for root), collapse
        # it into ourself and return the path we collapsed.
        if len(self.children) == 1:
            old_path, child = self.children.values()[0]
            if child.entries == self.entries:
                self.children = child.children
                return old_path

    def search(self, word):
        """Return a set of all data entry ids represented by prefix `word`.
        Returns an empty set if this prefix is not in the Trie.
        """
        if word:
            # Get the candidate path to the remaining postfix of the
            # word, if any.
            path, child = self.children.get(word[0], ('', None))

            # If the candidate path prefixes our word or our word prefixes
            # the candidate path, search from that child using the word
            # with the path sliced off (empty string if path is longer).
            if (path and word.startswith(path)) or path.startswith(word):
                return child.search(word[len(path):])

            # Otherwise, the Radix Trie does not contain this word (prefix).
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
