# reset_db.py

from utils.db import get_connection, init_db

# Ensure table exists
init_db()

# Now safely delete data
conn = get_connection()
cursor = conn.cursor()

# Clear all characters
cursor.execute("DELETE FROM characters;")

# Optional: Reset auto-increment sequence
cursor.execute("DELETE FROM sqlite_sequence WHERE name='characters';")

conn.commit()
conn.close()

print("✅ Characters table cleared.")
