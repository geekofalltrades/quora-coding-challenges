import unittest
from search import TypeAheadSearchSession


class TestAddDeleteCommands(unittest.TestCase):
    """Test the add and delete methods of the search session class."""

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

    def test_add_no_punctuation_blobs(self):
        """Words that are blobs of punctuation aren't added to the Trie."""
        self.search.add("question q1 0.3 What the #@&%, man?")
        for s in set('#@&%,'[i:j] for i in range(5) for j in range(i, 6)):
            self.assertNotIn(s, self.search.trie)

    def test_delete(self):
        """Deleting removes elements from entries and the Trie."""
        # Repeat so we have some minimal confidence that the WeakSet
        # at each Trie node is dropping entries in a timely fashion.
        for i in range(100):
            self.search.add("question q1 0.3 How do I door?")
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


class TestQueryCommand(unittest.TestCase):
    """Test the query method of the search session class."""

    def setUp(self):
        self.search = TypeAheadSearchSession()
        self.search.add("question q1 0.3 This is a question.")
        self.search.add("user u1 0.3 Blargh Blarghson")

    def test_query_single_whole_term(self):
        """Retrieve an entry by searching a whole term."""
        result = self.search.query("10 question")
        self.assertEqual(len(result), 1)
        self.assertIn(self.search.entries['q1'], result)

    def test_query_single_prefix(self):
        """Retrieve an entry with a prefix of one of its search tokens."""
        result = self.search.query("10 ques")
        self.assertEqual(len(result), 1)
        self.assertIn(self.search.entries['q1'], result)

    def test_query_no_prefix(self):
        """Results can't be retrieved with substrings that aren't prefixes."""
        result = self.search.query("10 uest")
        self.assertEqual(len(result), 0)

        result = self.search.query("10 tion")
        self.assertEqual(len(result), 0)

    def test_query_multiple_terms(self):
        """Retrieve an entry by searching multiple terms."""
        result = self.search.query("10 this question")
        self.assertEqual(len(result), 1)
        self.assertIn(self.search.entries['q1'], result)

    def test_query_multiple_prefixes(self):
        """Retrieve an entry by searching multiple prefixes."""
        result = self.search.query("10 thi ques")
        self.assertEqual(len(result), 1)
        self.assertIn(self.search.entries['q1'], result)

    def test_query_mixed_term_and_prefix(self):
        """Retrieve an entry by searching both full terms and prefixes."""
        result = self.search.query("10 this is ques")
        self.assertEqual(len(result), 1)
        self.assertIn(self.search.entries['q1'], result)

    def test_query_non_prefix(self):
        """Results can't be retrieved when one search term isn't a prefix."""
        result = self.search.query("10 this uest")
        self.assertEqual(len(result), 0)

    def test_query_retrieve_multiple_results(self):
        """Retrieve multiple results, in the correct order."""
        self.search.add("question q2 0.5 This is another question.")
        self.search.add("question q3 0.4 This is a third question.")
        result = self.search.query("10 question")
        self.assertEqual(len(result), 3)
        self.assertIs(result[0], self.search.entries['q2'])
        self.assertIs(result[1], self.search.entries['q3'])
        self.assertIs(result[2], self.search.entries['q1'])

    def test_query_limit_result_count(self):
        """Limit the number of results retrieved."""
        self.search.add("question q2 0.5 This is another question.")
        self.search.add("question q3 0.4 This is a third question.")

        result = self.search.query("1 question")
        self.assertEqual(len(result), 1)
        self.assertIs(result[0], self.search.entries['q2'])

        result = self.search.query("2 question")
        self.assertEqual(len(result), 2)
        self.assertIs(result[0], self.search.entries['q2'])
        self.assertIs(result[1], self.search.entries['q3'])


class TestWqueryCommand(unittest.TestCase):
    """Test the wquery method of the search session class."""

    def setUp(self):
        self.search = TypeAheadSearchSession()
        self.search.add("question q1 0.3 This is a question.")
        self.search.add("question q2 0.6 This is another question.")
        self.search.add("question q3 0.4 This is a third question.")
        self.search.add("user u1 0.5 Question Questionson")

    def test_no_boosts(self):
        """Wquery is effectively a query when no boosts are applied."""
        self.assertEqual(
            self.search.query("3 question"),
            self.search.wquery("3 0 question")
        )

    def test_no_boosts_multiple_terms(self):
        """Wquery works with no boosts and multiple search terms."""
        self.assertEqual(
            self.search.query("3 this question"),
            self.search.wquery("3 0 this question")
        )

    def test_boost_type(self):
        """Boosting a type modifies the order of results."""
        result = self.search.wquery("2 1 user:2.0 question")
        self.assertEqual(self.search.entries['u1'], result[0])
        self.assertEqual(self.search.entries['q2'], result[1])

    def test_boost_type_multiple_times(self):
        """Boosting a type more than once multiplies the boosts."""
        # These boosts undo each other.
        result = self.search.wquery("2 2 user:2.0 user:0.5 question")
        self.assertEqual(self.search.entries['q2'], result[0])
        self.assertEqual(self.search.entries['u1'], result[1])

    def test_boost_id(self):
        """Boosting an id modifies the order of results."""
        result = self.search.wquery("2 1 u1:2.0 question")
        self.assertEqual(self.search.entries['u1'], result[0])
        self.assertEqual(self.search.entries['q2'], result[1])

    def test_boost_id_multiple_times(self):
        """Boosting an id more than once multiplies the boosts."""
        # These boosts undo each other.
        result = self.search.wquery("2 2 u1:2.0 u1:0.5 question")
        self.assertEqual(self.search.entries['q2'], result[0])
        self.assertEqual(self.search.entries['u1'], result[1])

    def test_boost_id_and_type(self):
        """Boosts of type and id are multiplied."""
        result = self.search.wquery(
            "2 3 question:2.0 user:2.0 u1:2.0 question"
        )
        self.assertEqual(self.search.entries['u1'], result[0])
        self.assertEqual(self.search.entries['q2'], result[1])

    def test_multiple_boosts_and_terms(self):
        """Wquery works with multiple boosts and search terms."""
        result = self.search.wquery(
            "2 2 question:2.0 q3:2.0 this question"
        )
        self.assertEqual(self.search.entries['q3'], result[0])
        self.assertEqual(self.search.entries['q2'], result[1])

if __name__ == '__main__':
    unittest.main()
