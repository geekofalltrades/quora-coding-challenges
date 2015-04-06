import sys


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

        # Rules are stored in a list where list index corresponds to
        # browser height for that rule.
        self.rules = []

    def update(self, update_time):
        """Update internal state based on the current time."""

    def _build_rules(self):
        """Build a set of dynamic programming rules for selecting stories."""
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

    def add_story(self, story_time, story_score, story_height):
        """Add a story."""
        self.update(story_time)

    def refresh(self, refresh_time):
        """Refresh the page."""
        self.update(refresh_time)


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
