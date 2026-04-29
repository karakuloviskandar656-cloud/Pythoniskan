import psycopg2
from config import load_config

commands = [
    """
    CREATE TABLE IF NOT EXISTS players (
        id       SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS game_sessions (
        id            SERIAL PRIMARY KEY,
        player_id     INTEGER REFERENCES players(id),
        score         INTEGER   NOT NULL,
        level_reached INTEGER   NOT NULL,
        played_at     TIMESTAMP DEFAULT NOW()
    )
    """
]

conn = psycopg2.connect(**load_config())
cur = conn.cursor()
for cmd in commands:
    cur.execute(cmd)
conn.commit()
cur.close()
conn.close()
print("Tables created successfully.")