import unittest
from search import TypeAheadRadixTrie


class TestRadixTrie(unittest.TestCase):
    def setUp(self):
        self.trie = TypeAheadRadixTrie()
        self.ids = ('u1', 't1')

    def test_contains(self):
        """Stored words are `in` the Trie."""
        self.trie.add('car', self.ids[0])
        self.assertIn('car', self.trie)

    def test_contains_no_prefix(self):
        """Prefixes of stored words are not `in` the Trie."""
        self.trie.add('cartel', self.ids[0])
        self.assertNotIn('car', self.trie)

    def test_contains_prefix_and_whole_word(self):
        """A stored word and stored prefix of that word are both `in` the Trie.
        """
        self.trie.add('car', self.ids[0])
        self.trie.add('cartel', self.ids[1])
        self.assertIn('car', self.trie)
        self.assertIn('cartel', self.trie)

    def test_add_word(self):
        """The Trie takes on the expected form when a word is added."""
        self.trie.add('some', self.ids[0])

        node = self.trie
        self.assertEqual(len(node.children), 1)
        self.assertIn('some', node.children)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.ids[0], node.entries)

        node = node.children['some']
        self.assertEqual(len(node.children), 0)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.ids[0], node.entries)

    def test_add_second_word(self):
        """The Trie takes on the expected form when a second word is added."""
        self.trie.add('some', self.ids[0])
        self.trie.add('day', self.ids[1])

        node = self.trie
        self.assertEqual(len(node.children), 2)
        self.assertIn('some', node.children)
        self.assertIn('day', node.children)
        self.assertEqual(len(node.entries), 2)
        for id in self.ids:
            self.assertIn(id, node.entries)

        node = self.trie.children['some']
        self.assertEqual(len(node.children), 0)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.ids[0], node.entries)

        node = self.trie.children['day']
        self.assertEqual(len(node.children), 0)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.ids[1], node.entries)

    def test_add_overlapping_word(self):
        """Add two overlapping words to the Trie."""
        self.trie.add('somebody', self.ids[0])
        self.trie.add('someday', self.ids[1])

        node = self.trie
        self.assertEqual(len(node.children), 1)
        self.assertIn('some', node.children)
        self.assertEqual(len(node.entries), 2)
        for id in self.ids:
            self.assertIn(id, node.entries)

        node = node.children['some']
        split_node = node
        self.assertEqual(len(node.children), 2)
        self.assertIn('body', node.children)
        self.assertIn('day', node.children)
        self.assertEqual(len(node.entries), 2)
        for id in self.ids:
            self.assertIn(id, node.entries)

        node = split_node.children['body']
        self.assertEqual(len(node.children), 0)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.ids[0], node.entries)

        node = split_node.children['day']
        self.assertEqual(len(node.children), 0)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.ids[1], node.entries)

    def test_two_ids_same_word(self):
        """Add two ids to the same word."""
        self.trie.add('some', self.ids[0])
        self.trie.add('some', self.ids[1])

        node = self.trie
        self.assertEqual(len(node.children), 1)
        self.assertIn('some', node.children)
        self.assertEqual(len(node.entries), 2)
        self.assertIn(self.ids[0], node.entries)
        self.assertIn(self.ids[1], node.entries)

        node = node.children['some']
        self.assertEqual(len(node.children), 0)
        self.assertEqual(len(node.entries), 2)
        self.assertIn(self.ids[0], node.entries)
        self.assertIn(self.ids[1], node.entries)

    def test_delete_only_word(self):
        """Delete the only entry/word from the Trie."""
        self.trie.add('some', self.ids[0])
        self.trie.delete('some', self.ids[0])
        self.assertEqual(len(self.trie.children), 0)
        self.assertEqual(len(self.trie.entries), 0)

    def test_delete_words_remaining(self):
        """Delete an entry from a Trie with multiple words."""
        self.trie.add('some', self.ids[0])
        self.trie.add('day', self.ids[1])
        self.trie.delete('some', self.ids[0])

        node = self.trie
        self.assertEqual(len(node.children), 1)
        self.assertIn('day', node.children)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.ids[1], node.entries)

        node = node.children['day']
        self.assertEqual(len(node.children), 0)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.ids[1], node.entries)

    def test_delete_word_with_multiple_entries(self):
        """Delete an entry from a word that has multiple entries."""
        self.trie.add('some', self.ids[0])
        self.trie.add('some', self.ids[1])
        self.trie.delete('some', self.ids[0])

        node = self.trie
        self.assertEqual(len(node.children), 1)
        self.assertIn('some', node.children)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.ids[1], node.entries)

        node = node.children['some']
        self.assertEqual(len(node.children), 0)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.ids[1], node.entries)

    def test_delete_only_entry_from_postfix(self):
        """Delete the only entry from a word that postfixes another word."""
        self.trie.add('some', self.ids[0])
        self.trie.add('someday', self.ids[1])
        self.trie.delete('someday', self.ids[1])

        node = self.trie
        self.assertEqual(len(node.children), 1)
        self.assertIn('some', node.children)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.ids[0], node.entries)

        node = node.children['some']
        self.assertEqual(len(node.children), 0)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.ids[0], node.entries)

    def test_delete_postfix_collapse_branch(self):
        """Delete the only entry from a word that is one of two postfixing
        another word.
        """
        self.trie.add('somebody', self.ids[0])
        self.trie.add('someday', self.ids[1])
        self.trie.delete('someday', self.ids[1])

        node = self.trie
        self.assertEqual(len(node.children), 1)
        self.assertIn('somebody', node.children)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.ids[0], node.entries)

        node = node.children['somebody']
        self.assertEqual(len(node.children), 0)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.ids[0], node.entries)

    def test_delete_only_entry_from_prefix(self):
        """Delete the only entry from a word that prefixes another word."""
        self.trie.add('some', self.ids[0])
        self.trie.add('someday', self.ids[1])
        self.trie.delete('some', self.ids[0])

        node = self.trie
        self.assertEqual(len(node.children), 1)
        self.assertIn('someday', node.children)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.ids[0], node.entries)

        node = node.children['someday']
        self.assertEqual(len(node.children), 0)
        self.assertEqual(len(node.entries), 1)
        self.assertIn(self.ids[0], node.entries)

    def test_single_search(self):
        """Search for an entry at some word."""
        self.trie.add('some', self.ids[0])
        result = self.trie.search('some')
        self.assertEqual(len(result), 1)
        self.assertIn(self.ids[0], result)

    def test_single_search_prefix(self):
        """Search for an entry with a prefix of its word."""
        self.trie.add('some', self.ids[0])
        result = self.trie.search('som')
        self.assertEqual(len(result), 1)
        self.assertIn(self.ids[0], result)

    def test_single_search_non_prefix(self):
        """Search for an entry with a term that isn't a prefix."""
        self.trie.add('some', self.ids[0])
        result = self.trie.search('ome')
        self.assertEqual(len(result), 0)

    def test_multiple_search(self):
        """Search a term with multiple ids."""
        self.trie.add('some', self.ids[0])
        self.trie.add('somebody', self.ids[1])
        result = self.trie.search('some')
        self.assertEqual(len(result), 2)
        self.assertIn(self.ids[0], result)
        self.assertIn(self.ids[1], result)

    def test_child_search(self):
        """Search a term for which a prefix also has ids."""
        self.trie.add('some', self.ids[0])
        self.trie.add('somebody', self.ids[1])
        result = self.trie.search('someb')
        self.assertEqual(len(result), 1)
        self.assertIn(self.ids[1], result)

    def test_multiple_ids_search(self):
        """Search a word which has two ids."""
        self.trie.add('some', self.ids[0])
        self.trie.add('some', self.ids[1])
        result = self.trie.search('some')
        self.assertEqual(len(result), 2)
        self.assertIn(self.ids[0], result)
        self.assertIn(self.ids[1], result)

if __name__ == '__main__':
    unittest.main()
