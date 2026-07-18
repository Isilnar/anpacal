"""
migrate_to_bcrypt.py
--------------------
Standalone migration script. Copies database.db → database_bcrypt.db and
hashes all plain-text passwords with bcrypt.

Usage:
    python scripts/migrate_to_bcrypt.py

Requirements:
    pip install flask-bcrypt   (or install -r requirements.txt)

Safety:
    - Aborts if database_bcrypt.db already exists (prevents accidental overwrite).
    - Never modifies database.db.
"""

import os
import shutil
import sqlite3
import sys

try:
    from flask_bcrypt import generate_password_hash
except ImportError:
    print("ERROR: flask-bcrypt is not installed. Run: pip install flask-bcrypt==1.0.1")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DB = os.path.join(BASE_DIR, "database.db")
DST_DB = os.path.join(BASE_DIR, "database_bcrypt.db")


def main():
    # Verify source exists
    if not os.path.exists(SRC_DB):
        print(f"ERROR: Source database not found: {SRC_DB}")
        sys.exit(1)

    # Abort if destination already exists
    if os.path.exists(DST_DB):
        print(f"ERROR: Destination already exists: {DST_DB}")
        print("Remove it manually before running this script.")
        sys.exit(1)

    # Copy database
    print(f"Copying {SRC_DB} -> {DST_DB} ...")
    shutil.copy2(SRC_DB, DST_DB)

    # Hash all passwords
    conn = sqlite3.connect(DST_DB)
    cursor = conn.cursor()

    cursor.execute("SELECT id, password FROM user")
    users = cursor.fetchall()
    count = 0

    for user_id, plain_password in users:
        if plain_password:
            hashed = generate_password_hash(plain_password).decode("utf-8")
            cursor.execute("UPDATE user SET password = ? WHERE id = ?", (hashed, user_id))
            count += 1

    conn.commit()
    conn.close()

    print(f"Done. Migrated {count} user(s) to bcrypt hashes in {DST_DB}")
    print("Next step: set USE_BCRYPT = True in instance/config.py to use the new database.")


if __name__ == "__main__":
    main()
