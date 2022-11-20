import os
import csv
import datetime
import requests
import shutil
from dotenv import load_dotenv


load_dotenv()
_ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
_CHANNEL = os.getenv("CHANNEL")
_CLIENT_ID = os.getenv("CLIENT_ID")

_DATA_CSV = "focus"
_SUMMARY_CSV = "sumary"
_TWITCH_STREAM_API_ENDPOINT = "https://api.twitch.tv/helix/streams?{}"


def _is_streaming() -> bool:
    """Checks if the streamer is live on Twitch."""
    url = _TWITCH_STREAM_API_ENDPOINT.format("user_login=%s" % _CHANNEL)
    headers = {
        "Authorization": "Bearer %s" % _ACCESS_TOKEN,
        "Client-Id": _CLIENT_ID,
    }
    response = requests.get(url, headers=headers)
    return bool(response.json()["data"])


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
                    _tally_focus_counts(last_local.year, last_local.month)
                    _rotate_files(last_local.year, last_local.month)
                # Return early since we just need to check a single timestamp.
                return
    except FileNotFoundError:
        # no-op: This is acceptable if the file does not exist.
        return


def _convert_to_local_datetime(timestamp):
    """Converts the datetime by adding in the timezone difference."""
    return timestamp + timestamp.tzinfo.utcoffset(timestamp)


def _tally_focus_counts(year: int, month: int):
    """Tallies focus commands once per user per day.

    The tallying must happen before rotating the file.

    Args:
      year: The 4 digit number representing the year.
      month: The month as a number. This will be formatted to MM.
    """
    # dictionary of author and a list of dates
    tallies: Dict[str, Union[Set[str], List[str]]] = {}
    with open(f"{_DATA_CSV}.csv", "r", newline="") as csvfile:
        data_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        for row in data_reader:
            author = row[0]
            timestamp = datetime.datetime.fromisoformat(row[1])
            local_timestamp = _convert_to_local_datetime(timestamp)

            date = local_timestamp.strftime("%Y-%m-%d")
            tallies.setdefault(author, [])
            tallies[author].append(date)

    # This helps remove duplicate dates.
    for author, dates in tallies.items():
        tallies[author] = set(dates)

    month = "{:02d}".format(month)
    with open(f"{_SUMMARY_CSV}_{year}_{month}.csv", "a", newline="") as csvfile:
        data_writer = csv.writer(csvfile, delimiter=",", quotechar='"')
        for author, date_count in tallies.items():
            data_writer.writerow([author, len(date_count)])


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
    if not _is_streaming():
        # The streamer is not live, do not write a focus.
        return

    _maybe_rotate_files(timestamp)
    with open(f"{_DATA_CSV}.csv", "a", newline="") as csvfile:
        data_writer = csv.writer(csvfile, delimiter=",", quotechar='"')
        data_writer.writerow([author, timestamp.isoformat(), message])
