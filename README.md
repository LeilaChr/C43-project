# MyBnB

CSCC43 final project.

## Install dependencies

```
poetry install
poetry run python install_nltk.py
```

## Populate database

```
$ mysql
mysql> source sql/drop.sql
mysql> source sql/create.sql
mysql> source sql/populate.sql
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
