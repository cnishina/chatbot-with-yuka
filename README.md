# Focus chatbot

This chatbot listens to the focus command and writes it to a `focus.csv` file.
If the file does not exist, it will be created. Rotates the `focus.csv` file on
month or year not matching up. The rotation uses UTC timestamps.

> Example:
> 
> chat sends:
>
> ```
> !focus Creating a chatbot for yuka.
> ```
> 
> The `focus.csv` file should contain:
> 
> ```
> bedtimebear_808,2022-10-09T20:58:57.965000,Creating a chatbot for yuka.
> ```

# Getting started

Create a new twitch account that you'll use as the chat bot. Maybe something
called "yuka_bot" or "bot_with_yuka"? Next you will navigate to
https://dev.twitch.tv/console create an application.

Next navigate to the following URL (replacing the `<your client id>` with
the client id from the application).

```
https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=<your client id>&redirect_uri=http://localhost:3000&scope=chat%3Aread+chat%3Aedit
```

This will redirect to a URL that looks something like this:

```
http://localhost:3000/#access_token=<access_token>&scope=chat%3Aread+chat%3Aedit&token_type=bearer
```

Create a .env file at the root of this project and copy the `<access_token>`
from the URL string. In addition, add in the `<channel>` where the bot should
send messages. This should look as follows:

```
ACCESS_TOKEN=<access_token>
CHANNEL=<channel>
```

## Running chatbot with poetry

```
poetry install
poetry shell
python3 main.py
```

## Running chatbot with a virutal env:

```
python3 -m venv .
source bin/activate
pip install -r requirements.txt
python3 main.py
```

## Running unit tests

```
python -m unittest focus_test.py
```
