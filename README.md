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
```