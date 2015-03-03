import unittest
from trie import TypeaheadSearchTrie
from search import Entry


class TestTrie(unittest.TestCase):
    def setUp(self):
        self.trie = TypeaheadSearchTrie()
        self.entries = [
            Entry('user', 'u1', 0, 'Some user'),
            Entry('topic', 't1', 0, 'Some topic'),
        ]

    def test_add_word(self):
        """The Trie takes on the expected form when a word is added."""
        self.trie.add('some', self.entries[0])

        node = self.trie
        self.assertEqual(len(node.children), 1)
        self.assertIn('s', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['s']
        self.assertEqual(len(node.children), 1)
        self.assertIn('o', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['o']
        self.assertEqual(len(node.children), 1)
        self.assertIn('m', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['m']
        self.assertEqual(len(node.children), 1)
        self.assertIn('e', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['e']
        self.assertEqual(len(node.children), 0)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.entries[0], node.entries)

    def test_add_second_word(self):
        """The Trie takes on the expected form when a second word is added."""
        self.trie.add('some', self.entries[0])
        self.trie.add('day', self.entries[1])

        node = self.trie
        self.assertEqual(len(node.children), 2)
        self.assertIn('s', node.children)
        self.assertIn('d', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['s']
        self.assertEqual(len(node.children), 1)
        self.assertIn('o', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['o']
        self.assertEqual(len(node.children), 1)
        self.assertIn('m', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['m']
        self.assertEqual(len(node.children), 1)
        self.assertIn('e', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['e']
        self.assertEqual(len(node.children), 0)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.entries[0], node.entries)

        node = self.trie.children['d']
        self.assertEqual(len(node.children), 1)
        self.assertIn('a', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['a']
        self.assertEqual(len(node.children), 1)
        self.assertIn('y', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['y']
        self.assertEqual(len(node.children), 0)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.entries[1], node.entries)

    def test_add_overlapping_word(self):
        """Add two overlapping words to the Trie."""
        self.trie.add('somebody', self.entries[0])
        self.trie.add('someday', self.entries[1])

        node = self.trie
        self.assertEqual(len(node.children), 1)
        self.assertIn('s', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['s']
        self.assertEqual(len(node.children), 1)
        self.assertIn('o', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['o']
        self.assertEqual(len(node.children), 1)
        self.assertIn('m', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['m']
        self.assertEqual(len(node.children), 1)
        self.assertIn('e', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['e']
        self.assertEqual(len(node.children), 2)
        self.assertIn('d', node.children)
        self.assertIn('b', node.children)
        self.assertEqual(len(node.entries), 0)

    def test_two_entries_same_word(self):
        """Add two words to the same entry."""
        self.trie.add('some', self.entries[0])
        self.trie.add('some', self.entries[1])

        node = self.trie
        self.assertEqual(len(node.children), 1)
        self.assertIn('s', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['s']
        self.assertEqual(len(node.children), 1)
        self.assertIn('o', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['o']
        self.assertEqual(len(node.children), 1)
        self.assertIn('m', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['m']
        self.assertEqual(len(node.children), 1)
        self.assertIn('e', node.children)
        self.assertEqual(len(node.entries), 0)

        node = node.children['e']
        self.assertEqual(len(node.children), 0)
        self.assertEqual(len(node.entries), 2)
        self.assertIn(self.entries[0], node.entries)
        self.assertIn(self.entries[1], node.entries)

    def test_single_search(self):
        """Search for an entry at some word."""
        self.trie.add('some', self.entries[0])
        result = self.trie.search('some')
        self.assertEqual(len(result), 1)
        self.assertIn(self.entries[0], result)

    def test_multiple_search(self):
        """Search a term with multiple entries."""
        self.trie.add('some', self.entries[0])
        self.trie.add('somebody', self.entries[1])
        result = self.trie.search('some')
        self.assertEqual(len(result), 2)
        self.assertIn(self.entries[0], result)
        self.assertIn(self.entries[1], result)

    def test_child_search(self):
        """Search a term for which a prefix also has entries."""
        self.trie.add('some', self.entries[0])
        self.trie.add('somebody', self.entries[1])
        result = self.trie.search('someb')
        self.assertEqual(len(result), 1)
        self.assertIn(self.entries[1], result)

    def test_multiple_entries_search(self):
        """Search a word which has two entries."""
        self.trie.add('some', self.entries[0])
        self.trie.add('some', self.entries[1])
        result = self.trie.search('some')
        self.assertEqual(len(result), 2)
        self.assertIn(self.entries[0], result)
        self.assertIn(self.entries[1], result)

if __name__ == '__main__':
    unittest.main()
