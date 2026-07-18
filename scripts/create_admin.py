"""
create_admin.py
---------------
Creates (or replaces) the superadmin user with bcrypt-hashed password
and assigns the 'admin' role.

Usage:
    python scripts/create_admin.py

Requires the Flask app context (instance/config.py + .env must exist).
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import bcrypt, create_app, db
from app.infrastructure.role.orm import RoleORM
from app.infrastructure.user.orm import UserORM, UserRoleAssociation

USERNAME = "superadmin"
PASSWORD = "MasterIA.123"


def main():
    app = create_app()
    with app.app_context():
        # 1. Ensure 'admin' role exists
        role = RoleORM.query.filter_by(name="admin").first()
        if role is None:
            role = RoleORM(name="admin", description="Administrador")
            db.session.add(role)
            db.session.flush()
            print("[+] Created 'admin' role")
        else:
            print("[=] 'admin' role already exists")

        # 2. Find or create user
        user = UserORM.query.filter_by(username=USERNAME).first()
        if user is not None:
            print(f"[~] User '{USERNAME}' exists (id={user.id}) — replacing password")
        else:
            user = UserORM()
            user.username = USERNAME
            user.name = "Super"
            user.surname = "Admin"
            user.status = 1
            db.session.add(user)
            db.session.flush()
            print(f"[+] Created user '{USERNAME}' (id={user.id})")

        # 3. Set bcrypt password
        user.password = bcrypt.generate_password_hash(PASSWORD).decode("utf-8")
        user.update_token()

        # 4. Ensure admin role association
        assoc = UserRoleAssociation.query.filter_by(user_id=user.id, role_id=role.id).first()
        if assoc is None:
            assoc = UserRoleAssociation(user_id=user.id, role_id=role.id)
            db.session.add(assoc)
            print("[+] Assigned 'admin' role to user")
        else:
            print("[=] User already has 'admin' role")

        db.session.commit()
        print(f"\n✓ Done. Login with: {USERNAME} / {PASSWORD}")


if __name__ == "__main__":
    main()
