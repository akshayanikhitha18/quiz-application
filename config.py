import os
# Edit the password below (or set the DB_PASSWORD environment variable)
DB = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "Akshaya88.."),
    "database": "quizsphere",
}
