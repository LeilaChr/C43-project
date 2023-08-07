# MyBnB

CSCC43 final project.

## Install dependencies

```
poetry install
poetry run python install_nltk.py
```

## Start server

Choose one:

### Plain development server

```
poetry run python -m mybnb.app
```

### Auto-reloading debugger

```
poetry run flask --app mybnb/app.py --debug run
```
