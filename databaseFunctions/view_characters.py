import sqlite3

DB_NAME = "content_factory.db"

def view_characters():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, gender, description, voice_style, avatar_id FROM characters")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No characters found.")
        return

    for row in rows:
        print(f"\nID: {row[0]}")
        print(f"Name: {row[1]}")
        print(f"Gender: {row[2]}")
        print(f"Description: {row[3]}")
        print(f"Voice Style: {row[4]}")
        print(f"Avatar ID: {row[5]}")

if __name__ == "__main__":
    view_characters()
