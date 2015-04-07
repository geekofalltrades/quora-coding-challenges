import sys
from collections import namedtuple

Story = namedtuple('Story', ['id', 'time', 'score', 'height'])


class FeedOptimizerSession(object):
    """Class encapsulating the data needed for a single
    Feed Optimizer session.
    """
    def __init__(self, time_window, browser_height):
        self.time_window = time_window
        self.browser_height = browser_height

        # Stories are stored in buckets in descending order of score,
        # keyed by their browser height; and by their id.
        self.stories_by_bucket = {}
        self.stories_by_id = {}

        # id tracking for allocating new ids and for removing old stories.
        self.current_story_id = 0
        self.oldest_story_id = 1

        # Rules are stored in a list where list index corresponds to
        # browser height for that rule.
        self.rules = []

    def add_story(self, story_time, story_score, story_height):
        """Add a story."""
        self.current_story_id += 1
        new_story = Story(
            self.current_story_id,
            story_time,
            story_score,
            story_height
        )

        self.stories_by_id[new_story.id] = new_story

        bucket = self.stories_by_bucket.setdefault(new_story.height, [])
        i = 0
        while i < len(bucket):
            if new_story.score > bucket[i].score:
                bucket.insert(i, new_story)
                break
            i += 1
        else:
            bucket.append(new_story)

    def remove_story(self, story_id):
        """Remove the story with the given id."""
        story = self.stories_by_id[story_id]

        del self.stories_by_id[story_id]

        self.stories_by_bucket[story.height].remove(story)
        if not self.stories_by_bucket[story.height]:
            del self.stories_by_bucket[story.height]

    def refresh(self, refresh_time):
        """Refresh the page.
        Build a set of dynamic programming rules to determine optimal feed.
        """
        # For now, built from scratch every time.
        rules = [set()]

        for browser_height in range(1, self.browser_height + 1):
            possible_rules = []
            for story_height, story_bucket in \
                    self.stories_by_bucket.iteritems():
                # Skip this bucket if its story height is greater than
                # the browser height.
                if browser_height - story_height < 0:
                    continue

                previous_rule = rules[browser_height - story_height]

                # Find the highest-scoring story of this length not already
                # used in the previous_rule and add it to a new candidate rule.
                for story in story_bucket:
                    if story not in previous_rule:
                        possible_rules.append(previous_rule.copy())
                        possible_rules[-1].add(story)
                        break

            rules[browser_height] = max(
                possible_rules,
                key=lambda rule: sum(
                    self.stories_by_id[id].score for id in rule
                )
            )


def main():
    """The main feed optimizer loop."""
    num_events, time_window, height = sys.stdin.readline().strip().split()

    session = FeedOptimizerSession(time_window, height)

    for i in range(num_events):
        event = sys.stdin.readline().strip()

        if event[0] == 'S':
            session.add_story(*event[2:].split())
        elif event[0] == 'R':
            session.refresh(event[2:])
        else:
            raise ValueError("Unrecognized input format.")


if __name__ == '__main__':
    main()
