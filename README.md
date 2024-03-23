# Binarisation app

## What is this

The binarisation app allows to quickly gate individual markers TMAs.

## Installation

1. Clone the repository.
2. Copy the `.env` file with all credentials into the folder of the repository.
3. Run

```
docker-compose up -d --build
```

4. Open the url `http://localhost:5005/`

Populate the database:

```
python populate_db.py ~/Downloads/thresholds.csv validation thresholds --port 8888 --username devroot --password devroot
```
