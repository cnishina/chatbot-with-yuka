import os
import csv
import datetime
import shutil


_DATA_CSV = "focus.csv"


def _maybe_rotate_files(timestamp: datetime.datetime):
    """Maybe rotates the file based on the timestamp.

    If the year or month does not match the current chat message timestamp, then
    the file should be rotated. A limitation of this implementation is that it
    uses UTC time and not the local timezone when doing this comparison.

    Args:
      timestamp: The datetime to compare with the timestamp in the csv file.
    """
    try:
        with open(_DATA_CSV, "r", newline="") as csvfile:
            data_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            for row in data_reader:
                last_timestamp = datetime.datetime.fromisoformat(row[1])
                if (
                    last_timestamp.year != timestamp.year
                    or last_timestamp.month != timestamp.month
                ):
                    _rotate_files(last_timestamp.year, last_timestamp.month)
                # Return early since we just need to check a single timestamp.
                return
    except FileNotFoundError:
        # no-op: This is acceptable if the file does not exist.
        return


def _rotate_files(year: int, month: int):
    """Rotates the file and removes the original file.

    Args:
      year: The 4 digit number representing the year.
      month: The month as a number. This will be formatted to MM.
    """
    month = "{:02d}".format(month)
    shutil.copyfile(_DATA_CSV, f"focus_{year}_{month}.csv")
    os.remove(_DATA_CSV)


def write_focus(author: str, message: str, timestamp: datetime.datetime):
    """Writes focus message to a file.

    Args:
      author: The author of the focus message.
      message: The focus message without the focus command.
      timestamp: The timestamp of the message.
    """
    _maybe_rotate_files(timestamp)
    with open(_DATA_CSV, "a", newline="") as csvfile:
        data_writer = csv.writer(csvfile, delimiter=",", quotechar='"')
        data_writer.writerow([author, timestamp.isoformat(), message])
