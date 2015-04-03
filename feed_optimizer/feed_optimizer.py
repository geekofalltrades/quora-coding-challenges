import sys


class FeedOptimizerSession(object):
    """Class encapsulating the data needed for a single
    Feed Optimizer session.
    """
    def __init__(self, time_window, browser_height):
        self.time_window = time_window
        self.browser_height = browser_height
        self.stories = set()
        self.rules = []

    def update(self, update_time):
        """Update internal state based on the current time."""

    def _build_rules(self):
        """Build a set of dynamic programming rules for selecting stories."""

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
