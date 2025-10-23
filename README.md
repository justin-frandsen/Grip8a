# Grip8a

Repo for finger strength project

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Repo Size](https://img.shields.io/github/repo-size/justin-frandsen/Grip8a.svg)](https://github.com/justin-frandsen/Grip8a)
[![Last Commit](https://img.shields.io/github/last-commit/justin-frandsen/Grip8a.svg)](https://github.com/justin-frandsen/Grip8a/commits/main)

```
ls -l grip8a.db

# show users
sqlite3 grip8a.db "SELECT id, name FROM user;"

# show recent readings
sqlite3 grip8a.db "SELECT id, user_id, timestamp_iso, force FROM reading ORDER BY timestamp_ms DESC LIMIT 10;"

sqlite3 grip8a.db -header -column "SELECT r.id, r.user_id, u.name, r.timestamp_ms, r.timestamp_iso, r.force FROM reading r JOIN user u ON r.user_id = u.id WHERE u.name = 'micah' COLLATE NOCASE ORDER BY r.timestamp_ms ASC;"

sqlite3 grip8a.db "ALTER TABLE user ADD COLUMN age INTEGER; ALTER TABLE user ADD COLUMN gender TEXT; ALTER TABLE user ADD COLUMN weight REAL; ALTER TABLE user ADD COLUMN notes TEXT;"
```

SQL (Structured Query Language) is the language used to talk to relational databases (SQLite, PostgreSQL, MySQL, etc.). You describe what data you want (declarative) rather than how to compute it.

Core statements
SELECT — read data

Basic: SELECT columns FROM table;
Example: SELECT id, name FROM user;
Select all columns (avoid in production): SELECT * FROM user;
INSERT — add rows

curl -sS http://127.0.0.1:8000/ | sed -n '1,120p'