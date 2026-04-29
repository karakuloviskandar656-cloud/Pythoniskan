import psycopg2
from config import load_config

def get_connection():
    """Return a new database connection."""
    return psycopg2.connect(**load_config())

def get_or_create_player(username):
    """Return the player_id for the given username. Insert if new."""
    conn = get_connection()
    cur = conn.cursor()
    # Try to insert; if username already exists, do nothing (ON CONFLICT)
    cur.execute(
        "INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO NOTHING",
        (username,)
    )
    # Now fetch the id
    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return row[0] if row else None

def save_game_session(username, score, level_reached):
    """Save a game session for the given player."""
    player_id = get_or_create_player(username)
    if player_id is None:
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
        (player_id, score, level_reached)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_top_leaderboard(limit=10):
    """Return list of (rank, username, score, level, date)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.username, gs.score, gs.level_reached, gs.played_at
        FROM game_sessions gs
        JOIN players p ON gs.player_id = p.id
        ORDER BY gs.score DESC
        LIMIT %s
        """,
        (limit,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # Add rank
    result = []
    for i, (uname, score, level, date) in enumerate(rows, 1):
        result.append((i, uname, score, level, date.strftime("%Y-%m-%d %H:%M")))
    return result

def get_personal_best(username):
    """Return the highest score for that username, or 0."""
    player_id = get_or_create_player(username)
    if player_id is None:
        return 0
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT MAX(score) FROM game_sessions WHERE player_id = %s",
        (player_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row and row[0] is not None else 0