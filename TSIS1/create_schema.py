import psycopg2
from config import load_config

commands = [
    """CREATE TABLE IF NOT EXISTS groups (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL
    )""",

    """ALTER TABLE contacts ADD COLUMN IF NOT EXISTS email VARCHAR(100)""",
    """ALTER TABLE contacts ADD COLUMN IF NOT EXISTS birthday DATE""",
    """ALTER TABLE contacts ADD COLUMN IF NOT EXISTS group_id INTEGER REFERENCES groups(id)""",
    """ALTER TABLE contacts ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now()""",

    """CREATE TABLE IF NOT EXISTS phones (
        id SERIAL PRIMARY KEY,
        contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
        phone VARCHAR(20) NOT NULL,
        type VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
    )""",

    """INSERT INTO groups (name) VALUES ('Family'), ('Work'), ('Friend'), ('Other')
       ON CONFLICT (name) DO NOTHING""",
]

conn = psycopg2.connect(**load_config())
cur = conn.cursor()
for cmd in commands:
    cur.execute(cmd)
conn.commit()
cur.close()
conn.close()
print("Schema updated successfully.")