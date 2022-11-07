import os
import csv
import datetime
import shutil


_DATA_CSV = "focus"


def _maybe_rotate_files(timestamp: datetime.datetime):
    """Maybe rotates the file based on the timestamp.

    If the year or month does not match the current chat message timestamp, then
    the file should be rotated.

    Args:
      timestamp: The datetime to compare with the timestamp in the csv file
    """
    try:
        with open(f"{_DATA_CSV}.csv", "r", newline="") as csvfile:
            data_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            for row in data_reader:
                last_timestamp = datetime.datetime.fromisoformat(row[1])
                last_local = _convert_to_local_datetime(last_timestamp)
                curr_local = _convert_to_local_datetime(timestamp)

                # Rotate files when the year / month are different.
                if (
                    last_local.year != curr_local.year
                    or last_local.month != curr_local.month
                ):
                    _rotate_files(last_local.year, last_local.month)
                # Return early since we just need to check a single timestamp.
                return
    except FileNotFoundError:
        # no-op: This is acceptable if the file does not exist.
        return


def _convert_to_local_datetime(timestamp):
    """Converts the datetime by adding in the timezone difference."""
    return timestamp + timestamp.tzinfo.utcoffset(timestamp)


def _rotate_files(year: int, month: int):
    """Rotates the file and removes the original file.

    Args:
      year: The 4 digit number representing the year.
      month: The month as a number. This will be formatted to MM.
    """
    month = "{:02d}".format(month)
    shutil.copyfile(f"{_DATA_CSV}.csv", f"{_DATA_CSV}_{year}_{month}.csv")
    os.remove(f"{_DATA_CSV}.csv")


def write_focus(author: str, message: str, timestamp: datetime.datetime):
    """Writes focus message to a file.

    Args:
      author: The author of the focus message.
      message: The focus message without the focus command.
      timestamp: The timestamp of the message (timestamp includes the
            timezone offset)
    """
    _maybe_rotate_files(timestamp)
    with open(f"{_DATA_CSV}.csv", "a", newline="") as csvfile:
        data_writer = csv.writer(csvfile, delimiter=",", quotechar='"')
        data_writer.writerow([author, timestamp.isoformat(), message])
