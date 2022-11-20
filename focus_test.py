import csv
import datetime
import os
import unittest

import focus

# This ensures that the file we write is not the default one.
# The prefix is for testing only.
focus._DATA_CSV = "test_focus"
focus._SUMMARY_CSV = "test_summary"

_TEST_FILE = "test_focus.csv"
_ROTATED_TEST_FILE = "test_focus_2022_09.csv"
_TEST_SUMMARY_FILE = "test_summary_2022_09.csv"


def initialize_file():
    """Creates the csv file with some data."""
    with open(f"{focus._DATA_CSV}.csv", "a", newline="") as csvfile:
        data_writer = csv.writer(csvfile, delimiter=",", quotechar='"')
        author = "mr bear"
        timestamp = datetime.datetime.fromisoformat(
            "2022-10-01T06:59:00.000000-07:00"
        )
        message = "Doing it and doing it and doing it well."
        for unused_count in range(3):
            data_writer.writerow([author, timestamp.isoformat(), message])


def remove_files():
    """Removes all the files."""
    try:
        os.remove(_TEST_FILE)
    except:
        # no-op: tries to remove the test file.
        pass
    try:
        os.remove(_ROTATED_TEST_FILE)
    except:
        # no-op: tries to remove the rotated file.
        pass
    try:
        os.remove(_TEST_SUMMARY_FILE)
    except:
        # no-op: tries to remove the summary file.
        pass


class FocusTest(unittest.TestCase):
    def setUp(self):
        initialize_file()

    def tearDown(self):
        remove_files()

    def test_maybe_rotate_files(self):
        tzinfo = datetime.timezone(datetime.timedelta(hours=-7))
        timestamp = datetime.datetime(
            year=2022, month=10, day=1, hour=7, minute=1, tzinfo=tzinfo
        )
        focus._maybe_rotate_files(timestamp)

        self.assertFalse(os.path.exists(_TEST_FILE))
        self.assertTrue(os.path.exists(_ROTATED_TEST_FILE))

    def test_write_focus(self):
        tzinfo = datetime.timezone(datetime.timedelta(hours=-7))
        timestamp = datetime.datetime(
            year=2022, month=10, day=1, hour=7, minute=1, tzinfo=tzinfo
        )

        def _is_streaming():
            return True

        focus._is_streaming = _is_streaming
        focus.write_focus(
            "mr bear's friend",
            "I represent Queens, she was raised out in Brooklyn.",
            timestamp,
        )

        # The rotated file has the 3 lines written to it.
        count = 0
        with open(_ROTATED_TEST_FILE, "r", newline="") as csvfile:
            data_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            for row in data_reader:
                count += 1
        self.assertEqual(count, 3)

        # The default file has the single line written with the focus command.
        count = 0
        with open(_TEST_FILE, "r", newline="") as csvfile:
            data_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            for row in data_reader:
                count += 1
        self.assertEqual(count, 1)

    def test_not_write_focus(self):
        tzinfo = datetime.timezone(datetime.timedelta(hours=-7))
        timestamp = datetime.datetime(
            year=2022, month=10, day=1, hour=7, minute=1, tzinfo=tzinfo
        )

        def _is_streaming():
            return False

        focus._is_streaming = _is_streaming
        focus.write_focus(
            "mr bear's friend",
            "I represent Queens, she was raised out in Brooklyn.",
            timestamp,
        )

        # The default file has not changed. The streamer is not live.
        count = 0
        with open(_TEST_FILE, "r", newline="") as csvfile:
            data_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            for row in data_reader:
                count += 1
        self.assertEqual(count, 3)

    def test_tally_focus_counts(self):
        # The test counts for September posts
        # The initialize_file writes the same focus command 3 times at 11:59 pm
        # on 2002/09/30.
        with open(f"{focus._DATA_CSV}.csv", "a", newline="") as csvfile:
            data_writer = csv.writer(csvfile, delimiter=",", quotechar='"')
            author = "mr bear's friend"
            timestamp = datetime.datetime.fromisoformat(
                "2022-09-10T06:59:00.000000-07:00"
            )
            message = "Doing it and doing it and doing it well."
            data_writer.writerow([author, timestamp.isoformat(), message])
            timestamp = datetime.datetime.fromisoformat(
                "2022-09-11T06:59:00.000000-07:00"
            )
            data_writer.writerow([author, timestamp.isoformat(), message])
            timestamp = datetime.datetime.fromisoformat(
                "2022-09-12T06:59:00.000000-07:00"
            )
            data_writer.writerow([author, timestamp.isoformat(), message])
            timestamp = datetime.datetime.fromisoformat(
                "2022-09-13T06:59:00.000000-07:00"
            )
            message = "I represent Queens, she was raised out in Brooklyn."
            data_writer.writerow([author, timestamp.isoformat(), message])
        focus._tally_focus_counts(2022, 9)

        tallies: Dict[str, int] = {}
        with open(_TEST_SUMMARY_FILE, "r", newline="") as csvfile:
            data_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            for row in data_reader:
                tallies[row[0]] = row[1]
        self.assertEqual(tallies["mr bear"], "1")
        self.assertEqual(tallies["mr bear's friend"], "4")


if __name__ == "__main__":
    unittest.main()
