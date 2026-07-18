"""
migrate_fernet.py
-----------------
Standalone migration script. Encrypts PII fields (number_id, email, phone)
in database_bcrypt.db using Fernet symmetric encryption and adds HMAC-SHA256
hash columns for dedup queries.

Usage:
    python scripts/migrate_fernet.py

Requirements:
    pip install cryptography python-dotenv

Safety:
    - Aborts if FERNET_KEY is not set in environment / .env
    - Aborts if database_bcrypt.db does not exist
    - Idempotent: rows already encrypted (Fernet token prefix 'gAAAAA') are skipped
    - NEVER touches database.db

Rollback:
    Restore database_bcrypt.db from backup taken before running this script.
    Setting USE_BCRYPT=False alone is NOT sufficient once rows are encrypted.
"""

import hashlib
import hmac
import os
import sqlite3
import sys

try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: python-dotenv is not installed. Run: pip install python-dotenv")
    sys.exit(1)

try:
    from cryptography.fernet import Fernet
except ImportError:
    print("ERROR: cryptography is not installed. Run: pip install cryptography")
    sys.exit(1)

# Load .env from project root (two levels up from scripts/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

FERNET_KEY = os.environ.get("FERNET_KEY", "")
DB_PATH = os.path.join(BASE_DIR, "database_bcrypt.db")


def get_fernet():
    key = FERNET_KEY
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)


def hash_field(fernet_key_bytes, value):
    return hmac.new(fernet_key_bytes, value.encode(), hashlib.sha256).hexdigest()


def main():
    # Guards
    if not FERNET_KEY:
        print("ERROR: FERNET_KEY is not set. Add it to .env before running this script.")
        sys.exit(1)

    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found: {DB_PATH}")
        print("Run migrate_to_bcrypt.py first, or ensure you are in the project root.")
        sys.exit(1)

    fernet = get_fernet()
    fernet_key_bytes = FERNET_KEY.encode() if isinstance(FERNET_KEY, str) else FERNET_KEY

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Add hash columns idempotently
    for col in ("number_id_hash", "email_hash"):
        try:
            cursor.execute(f"ALTER TABLE user ADD COLUMN {col} TEXT")
            print(f"Added column: {col}")
        except sqlite3.OperationalError:
            print(f"Column already exists (skipping): {col}")

    conn.commit()

    # Fetch rows
    cursor.execute("SELECT id, number_id, email, phone FROM user")
    rows = cursor.fetchall()

    migrated = 0
    skipped = 0

    for user_id, number_id, email, phone in rows:
        # Detect already-encrypted rows (Fernet token prefix)
        if number_id and number_id.startswith("gAAAAA"):
            skipped += 1
            continue

        # Encrypt fields (None-safe)
        enc_number_id = fernet.encrypt(number_id.encode()).decode() if number_id else number_id
        enc_email = fernet.encrypt(email.encode()).decode() if email else email
        enc_phone = fernet.encrypt(phone.encode()).decode() if phone else phone

        # Compute hashes (None-safe)
        hsh_number_id = hash_field(fernet_key_bytes, number_id) if number_id else None
        hsh_email = hash_field(fernet_key_bytes, email) if email else None

        cursor.execute(
            "UPDATE user SET number_id=?, email=?, phone=?, number_id_hash=?, email_hash=? WHERE id=?",
            (enc_number_id, enc_email, enc_phone, hsh_number_id, hsh_email, user_id),
        )
        migrated += 1

    conn.commit()

    user_migrated = migrated
    user_skipped = skipped

    # ------------------------------------------------------------------ #
    # STUDENT TABLE
    # ------------------------------------------------------------------ #
    print("\n--- Migrating table: student ---")

    # Add number_id_hash column idempotently
    try:
        cursor.execute("ALTER TABLE student ADD COLUMN number_id_hash TEXT")
        print("Added column: number_id_hash (student)")
    except sqlite3.OperationalError:
        print("Column already exists (skipping): number_id_hash (student)")

    conn.commit()

    # Fetch student rows
    cursor.execute("SELECT id, number_id, email, phone, address FROM student")
    student_rows = cursor.fetchall()

    migrated = 0
    skipped = 0

    for student_id, number_id, email, phone, address in student_rows:
        # Detect already-encrypted rows (Fernet token prefix)
        if number_id and number_id.startswith("gAAAAA"):
            skipped += 1
            continue

        # Encrypt fields (None-safe)
        enc_number_id = fernet.encrypt(number_id.encode()).decode() if number_id else number_id
        enc_email = fernet.encrypt(email.encode()).decode() if email else email
        enc_phone = fernet.encrypt(phone.encode()).decode() if phone else phone
        enc_address = fernet.encrypt(address.encode()).decode() if address else address

        # Compute hash (None-safe)
        hsh_number_id = hash_field(fernet_key_bytes, number_id) if number_id else None

        cursor.execute(
            "UPDATE student SET number_id=?, email=?, phone=?, address=?, number_id_hash=? WHERE id=?",
            (enc_number_id, enc_email, enc_phone, enc_address, hsh_number_id, student_id),
        )
        migrated += 1

    conn.commit()
    conn.close()

    print("\nMigration complete.")
    print(f"  [user]    Migrated : {user_migrated} row(s)")
    print(f"  [user]    Skipped  : {user_skipped} row(s) (already encrypted)")
    print(f"  [student] Migrated : {migrated} row(s)")
    print(f"  [student] Skipped  : {skipped} row(s) (already encrypted)")
    print("\nIMPORTANT: Keep a backup of database_bcrypt.db and the FERNET_KEY.")
    print("There is NO recovery without both the key and a backup.")


if __name__ == "__main__":
    main()
