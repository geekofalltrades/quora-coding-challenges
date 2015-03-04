import unittest
from search import TypeAheadSearchSession


class TestTypeAheadSearchSession(unittest.TestCase):
    """Test the TypeAheadSearchSession class."""

    def setUp(self):
        self.search = TypeAheadSearchSession()

    def test_add(self):
        self.search.add("question q1 0.5 How do I even?")
        self.assertIn('q1', self.search.entries)

        entry = self.search.entries['q1']
        self.assertEqual(entry.type, 'question')
        self.assertEqual(entry.id, 'q1')
        self.assertEqual(entry.score, 0.5)
        self.assertEqual(entry.data, "How do I even?")

        self.assertIn('how', self.search.trie)
        self.assertIn('do', self.search.trie)
        self.assertIn('i', self.search.trie)
        self.assertIn('even', self.search.trie)

    def test_add_case_sensitivity(self):
        """Only lowercase tokens are added to the Trie."""
        self.search.add("question q1 0.3 I Am TwElVe Years Old.")
        self.assertTrue(all(
            s in self.search.trie
            for s in ('i', 'am', 'twelve', 'years', 'old'))
        )
        self.assertFalse(any(
            s in self.search.trie
            for s in ('I', 'Am', 'TwElVe', 'Years', 'Old'))
        )

    def test_add_strip_punctuation(self):
        """Punctuation is stripped from ends of tokens added to the Trie."""
        self.search.add("question q1 0.3 Some \"quotes\" and, also, commas.")

        self.assertIn('quotes', self.search.trie)
        self.assertNotIn('"quotes"', self.search.trie)

        self.assertIn('and', self.search.trie)
        self.assertIn('also', self.search.trie)
        self.assertNotIn('and,', self.search.trie)
        self.assertNotIn('also,', self.search.trie)

        self.assertIn('commas', self.search.trie)
        self.assertNotIn('commas.', self.search.trie)

    def test_add_center_punctuation_preserved(self):
        """Punctuation in the middle of words is preserved in the Trie."""
        self.search.add(
            "question q1 0.3"
            " Ph'nglui mglw'nafh Cthulhu R'lyeh wgah'nagl fhtagn."
        )
        self.assertTrue(all(
            s in self.search.trie
            for s in ("ph'nglui", "mglw'nafh", "r'lyeh", "wgah'nagl"))
        )
        self.assertFalse(any(
            s in self.search.trie
            for s in ("phnglui", "mglwnafh", "rlyeh", "wgahnagl"))
        )

    def test_delete(self):
        """Deleting removes elements from entries and the Trie."""
        # Repeat so we have some minimal confidence that the WeakSet
        # at each Trie node is dropping entries in a timely fashion.
        for i in range(100):
            self.search.add('question q1 0.3 How do I door?')
            self.assertTrue(all(
                s in self.search.trie
                for s in ('how', 'do', 'i', 'door'))
            )
            self.assertIn('q1', self.search.entries)
            self.search.delete('q1')
            self.assertFalse(any(
                s in self.search.trie
                for s in ('how', 'do', 'i', 'door'))
            )
            self.assertNotIn('q1', self.search.entries)

if __name__ == '__main__':
    unittest.main()
