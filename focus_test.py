import csv
import datetime
import os
import unittest
from freezegun import freeze_time

import focus

focus._DATA_CSV = "test_focus"  # This ensures that the file we write is not
                                # the default one. This is for testing only.

_TEST_FILE = "test_focus.csv"
_ROTATED_TEST_FILE = "test_focus_2022_09.csv"


def initialize_file():
    """Creates the csv file with some data."""
    with open(f"{focus._DATA_CSV}.csv", "a", newline="") as csvfile:
        data_writer = csv.writer(csvfile, delimiter=",", quotechar='"')
        author = "mr bear"
        timestamp = datetime.datetime.fromisoformat(
            "2022-09-09T21:00:27.430000"
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


class FocusTest(unittest.TestCase):
    def setUp(self):
        initialize_file()

    def tearDown(self):
        remove_files()

    @freeze_time("2022-10-01 01:00")
    def test_maybe_rotate_files(self):
        timestamp = datetime.datetime.now()
        focus._maybe_rotate_files(timestamp)

        self.assertFalse(os.path.exists(_TEST_FILE))
        self.assertTrue(os.path.exists(_ROTATED_TEST_FILE))

    @freeze_time("2022-09-12 01:00")
    def test_write_focus(self):
        timestamp = datetime.datetime.now()
        focus.write_focus(
            "mr bear's friend",
            "I represent Queens, she was raised out in Brooklyn.",
            timestamp,
        )
        count = 0
        with open(_TEST_FILE, "r", newline="") as csvfile:
            data_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            for row in data_reader:
                count += 1
        self.assertEqual(count, 4)


if __name__ == "__main__":
    unittest.main()
