import unittest
from feed_optimizer import FeedOptimizerSession


class TestFeedOptimizerSession(unittest.TestCase):
    """Test the FeedOptimizerSession."""
    def setUp(self):
        self.session = FeedOptimizerSession(10, 100)

    def test_add_story(self):
        """Stories are added to id and bucket dicts."""

    def test_add_story_collision(self):
        """Stories of the same height are bucketed together."""

    def test_add_story_collision_higher_score(self):
        """A colliding story with a higher score comes first in the bucket."""

    def test_add_story_collision_lower_score(self):
        """A colliding story with a lower score comes second in the bucket."""

    def test_add_story_collision_same_score(self):
        """A colliding story with the same score comes second in the bucket."""


if __name__ == '__main__':
    unittest.main()
