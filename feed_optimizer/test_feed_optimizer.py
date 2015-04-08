import unittest
from feed_optimizer import FeedOptimizerSession, Story


class TestFeedOptimizerSession(unittest.TestCase):
    """Test the FeedOptimizerSession."""
    def setUp(self):
        self.session = FeedOptimizerSession(10, 100)

    def test_add_story(self):
        """Stories are added to id and bucket dicts."""
        # Add first story.
        self.session.add_story(10, 20, 30)

        # We have one story and it has id 1.
        self.assertEqual(1, len(self.session.stories_by_id))
        self.assertIn(1, self.session.stories_by_id)
        self.assertEqual(1, self.session.current_story_id)

        # The first story is a Story with expected attributes.
        story = self.session.stories_by_id[1]
        self.assertIsInstance(story, Story)
        self.assertEqual(story.id, 1)
        self.assertEqual(story.time, 10)
        self.assertEqual(story.score, 20)
        self.assertEqual(story.height, 30)

        # We have one bucket containing only our story.
        self.assertEqual(1, len(self.session.stories_by_bucket))
        self.assertIn(30, self.session.stories_by_bucket)
        self.assertEqual(1, len(self.session.stories_by_bucket[30]))
        self.assertIn(
            story,
            self.session.stories_by_bucket[30]
        )

        # Add second story.
        self.session.add_story(11, 21, 31)

        # The bucket containing the first story is unaffected.
        self.assertEqual(1, len(self.session.stories_by_bucket[30]))

        # We have two stories and the second has id 2.
        self.assertEqual(2, len(self.session.stories_by_id))
        self.assertIn(2, self.session.stories_by_id)
        self.assertEqual(2, self.session.current_story_id)

        # The second story is a Story with expected attributes.
        story = self.session.stories_by_id[2]
        self.assertIsInstance(story, Story)
        self.assertEqual(story.id, 2)
        self.assertEqual(story.time, 11)
        self.assertEqual(story.score, 21)
        self.assertEqual(story.height, 31)

        # We have a second bucket containing only our second story.
        self.assertEqual(2, len(self.session.stories_by_bucket))
        self.assertIn(31, self.session.stories_by_bucket)
        self.assertEqual(1, len(self.session.stories_by_bucket[31]))
        self.assertIn(
            story,
            self.session.stories_by_bucket[31]
        )

    def test_add_story_collision(self):
        """Stories of the same height are bucketed together."""
        self.session.add_story(10, 20, 30)
        self.session.add_story(11, 21, 30)

        self.assertEqual(1, len(self.session.stories_by_bucket))
        self.assertIn(30, self.session.stories_by_bucket)
        self.assertEqual(2, len(self.session.stories_by_bucket[30]))
        self.assertIn(
            self.session.stories_by_id[1],
            self.session.stories_by_bucket[30]
        )
        self.assertIn(
            self.session.stories_by_id[2],
            self.session.stories_by_bucket[30]
        )

    def test_add_story_collision_higher_score(self):
        """A colliding story with a higher score comes first in the bucket."""
        self.session.add_story(10, 20, 30)
        self.session.add_story(11, 21, 30)

        self.assertEqual(
            self.session.stories_by_id[2],
            self.session.stories_by_bucket[30][0]
        )
        self.assertEqual(
            self.session.stories_by_id[1],
            self.session.stories_by_bucket[30][1]
        )

    def test_add_story_collision_lower_score(self):
        """A colliding story with a lower score comes second in the bucket."""
        self.session.add_story(10, 21, 30)
        self.session.add_story(11, 20, 30)

        self.assertEqual(
            self.session.stories_by_id[1],
            self.session.stories_by_bucket[30][0]
        )
        self.assertEqual(
            self.session.stories_by_id[2],
            self.session.stories_by_bucket[30][1]
        )

    def test_add_story_collision_same_score(self):
        """A colliding story with the same score comes second in the bucket."""
        self.session.add_story(10, 20, 30)
        self.session.add_story(11, 20, 30)

        self.assertEqual(
            self.session.stories_by_id[1],
            self.session.stories_by_bucket[30][0]
        )
        self.assertEqual(
            self.session.stories_by_id[2],
            self.session.stories_by_bucket[30][1]
        )

    def test_remove_story_by_id(self):
        """Removing a story removes it from the id dict."""
        self.session.add_story(10, 20, 30)
        self.session._remove_story(1)
        self.assertEqual(0, len(self.session.stories_by_id))

    def test_remove_story_empty_bucket(self):
        """Removing the only story in a bucket drops the bucket."""
        self.session.add_story(10, 20, 30)
        self.session.add_story(11, 21, 31)
        self.session._remove_story(1)
        self.assertEqual(1, len(self.session.stories_by_bucket))
        self.assertIn(31, self.session.stories_by_bucket)
        self.assertNotIn(30, self.session.stories_by_bucket)

    def test_remove_story_non_empty_bucket(self):
        """Removing a story from a bucket with other stories keeps the bucket.
        """
        self.session.add_story(10, 20, 30)
        self.session.add_story(11, 21, 31)
        self.session.add_story(12, 22, 30)
        self.session._remove_story(1)
        self.assertEqual(2, len(self.session.stories_by_bucket))
        self.assertIn(31, self.session.stories_by_bucket)
        self.assertIn(30, self.session.stories_by_bucket)
        self.assertEqual(1, len(self.session.stories_by_bucket[30]))
        self.assertEqual(1, len(self.session.stories_by_bucket[31]))

    def test_remove_story_missing_by_id(self):
        """A LookupError is raised when a story is missing from the id dict."""
        self.session.add_story(10, 20, 30)
        del self.session.stories_by_id[1]
        self.assertRaises(LookupError, self.session._remove_story, 1)

    def test_remove_story_missing_by_bucket(self):
        """A LookupError is raised when a story is missing from its bucket
        or its bucket is missing.
        """
        self.session.add_story(10, 20, 30)
        self.session.stories_by_bucket[30] = []
        self.assertRaises(LookupError, self.session._remove_story, 1)

        self.session.add_story(11, 21, 31)
        del self.session.stories_by_bucket[31]
        self.assertRaises(LookupError, self.session._remove_story, 2)

    def test_prune_stories_empty(self):
        """Pruning when empty has no effect."""
        self.session._prune_stories(0)
        self.assertEqual(1, self.session.oldest_story_id)

    def test_prune_stories_expired_stories(self):
        """Pruning removes expired stories and leaves valid stories."""
        self.session.add_story(10, 20, 30)
        self.session.add_story(11, 21, 31)
        self.session.add_story(12, 22, 32)

        self.session._prune_stories(11)

        self.assertEqual(2, self.session.oldest_story_id)
        self.assertNotIn(1, self.session.stories_by_id)
        self.assertIn(2, self.session.stories_by_id)
        self.assertIn(3, self.session.stories_by_id)

    def test_prune_stories_until_empty(self):
        """We can prune all stories if they are all expired."""
        self.session.add_story(10, 20, 30)
        self.session.add_story(11, 21, 31)
        self.session.add_story(12, 22, 32)

        self.session._prune_stories(13)

        self.assertEqual(4, self.session.oldest_story_id)
        self.assertEqual(0, len(self.session.stories_by_id))

    def test_build_rules_no_stories(self):
        """Building rules with no stories results in empty rules."""
        for rule in self.session._build_rules():
            self.assertEqual(set(), rule)

    def test_build_rules_single_story(self):
        """A single story appears only when it can be accommodated,
        appears in all rules after that, and appears only once.
        """
        self.session.add_story(10, 20, 30)
        story = self.session.stories_by_id[1]
        rules = self.session._build_rules()

        for i in range(30):
            self.assertEqual(set(), rules[i])

        for i in range(30, len(rules)):
            self.assertEqual({story}, rules[i])

    def test_build_rules_taller_better_story(self):
        """A higher-scoring, taller story overtakes a lower-scoring, shorter
        one when it fits.
        """
        self.session.add_story(10, 20, 30)
        short_story = self.session.stories_by_id[1]
        self.session.add_story(11, 30, 40)
        long_story = self.session.stories_by_id[2]
        rules = self.session._build_rules()

        for i in range(30):
            self.assertEqual(set(), rules[i])

        for i in range(30, 40):
            self.assertEqual({short_story}, rules[i])

        for i in range(40, 70):
            self.assertEqual({long_story}, rules[i])

        for i in range(70, len(rules)):
            self.assertEqual({long_story, short_story}, rules[i])

    def test_build_rules_shorter_better_story(self):
        """A higher-scoring, shorter story is preferred to a taller one until
        both fit.
        """
        self.session.add_story(10, 30, 30)
        short_story = self.session.stories_by_id[1]
        self.session.add_story(11, 20, 40)
        long_story = self.session.stories_by_id[2]
        rules = self.session._build_rules()

        for i in range(30):
            self.assertEqual(set(), rules[i])

        for i in range(30, 70):
            self.assertEqual({short_story}, rules[i])

        for i in range(70, len(rules)):
            self.assertEqual({short_story, long_story}, rules[i])

    def test_build_rules_same_height_same_score(self):
        """The older of two equal-height, equal-score stories is preferred."""
        self.session.add_story(10, 30, 30)
        old_story = self.session.stories_by_id[1]
        self.session.add_story(11, 30, 30)
        new_story = self.session.stories_by_id[2]
        rules = self.session._build_rules()

        for i in range(30):
            self.assertEqual(set(), rules[i])

        for i in range(30, 60):
            self.assertEqual({old_story}, rules[i])

        for i in range(60, len(rules)):
            self.assertEqual({old_story, new_story}, rules[i])

    def test_build_rules_prefer_higher_score(self):
        """Of two rules, prefer the rule with the higher score."""
        self.session.add_story(10, 20, 10)
        self.session.add_story(11, 20, 10)
        self.session.add_story(12, 50, 20)
        rules = self.session._build_rules()

        self.assertEqual({self.session.stories_by_id[3]}, rules[20])

    def test_build_rules_prefer_fewer_stories(self):
        """Of two rules with the same score, prefer the rule with fewer
        stories.
        """
        self.session.add_story(10, 20, 10)
        self.session.add_story(11, 20, 10)
        self.session.add_story(12, 40, 20)
        rules = self.session._build_rules()

        self.assertEqual({self.session.stories_by_id[3]}, rules[20])

    def test_build_rules_prefer_older_stories(self):
        """Of two rules with the same score and number of stories, prefer
        the rule with the lexicographically smaller ids (older set of stories).
        """
        self.session.add_story(10, 20, 10)
        self.session.add_story(11, 10, 5)
        self.session.add_story(12, 20, 10)
        self.session.add_story(13, 30, 15)
        rules = self.session._build_rules()

        self.assertEqual(
            {self.session.stories_by_id[1], self.session.stories_by_id[3]},
            rules[20]
        )

if __name__ == '__main__':
    unittest.main()
