# Flask Application Design

Important notes
- No Exposed MySQL Port: The connection string in app.py uses 'localhost' for secure database access
- startup Script (start.sh) : We manage MySQL initialization, schema loading, and Flask startup
- docker entrypoint support: Assumes your MySQL image uses /docker-entrypoint-initdb.d for initialization scripts
- adjust schema.sql, app.py (models, routes), and set your desired password
- countries.csv was last refreshed from https://datahub.io/core/country-list on 3/19/2024
