# Wordles

Wordles is a Flask web app that automatically collects urls for Wordle variants. It uses a few sources, including Wordle subreddits.

## Run

Install packages with [pip](https://pip.pypa.io/en/stable/).

```bash
pip install -r requirements.txt
```

Run flask app

```bash
flask run
```

## Config
Environment variables:

```bash
set FLASK_APP=flaskr
set FLASK_ENV=<environment>
set DATABASE_URL=<postgres database url>
set WDL_REDDIT_ID=<reddit client id>
set WDL_REDDIT_SECRET=<reddit client secret>
set WDL_SECRET_KEY=<secret key for security>
set WDL_ADDRESS_LIMIT=<limit for addresses stored, in case of database limits>
```

static/config/sources.txt

```txt
reddit wordle
...
<source> <info>
```

## Contributing
If you have any suggestions, feel free to open an issue.