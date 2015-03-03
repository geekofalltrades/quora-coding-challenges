"""A Trie (prefix tree) class for use in typeahead search.

Every node in the TypeAheadSearchTrie is another TypeAheadSearchTrie instance.
"""

from weakref import WeakSet


class TypeAheadSearchTrie(object):
    def __init__(self):
        # The children of this node. Because ordered traversals are not
        # important, these are stored in a dictionary.
        self.children = {}

        # Data entries associated with the word stored in the path to
        # this node. Stored in a WeakSet so that entries disappear
        # automatically when data entries are deleted.
        self.entries = WeakSet()

    def __contains__(self, word):
        if word:
            try:
                return self.children[word[0]].__contains__(word[1:])
            except KeyError:
                return False

        else:
            return bool(self.entries)

    def add(self, word, entry):
        """Adds the given data entry to the given Trie word.
        The word is created in the Trie if it doesn't already exist.
        """
        if word:
            self.children.setdefault(
                word[0],
                TypeAheadSearchTrie()
            ).add(word[1:], entry)

        else:
            self.entries.add(entry)

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
            return self.gather_entries()

    def gather_entries(self):
        """Gather all data entries stored in this node and its children."""
        entries = set(self.entries)
        for child in self.children.itervalues():
            entries.update(child.gather_entries())
        return entries
