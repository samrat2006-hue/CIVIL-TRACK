
import getpass
import sqlite3
from datetime import datetime
from pathlib import Path

from database.db_connection import get_connection
from modules.authentication import validate_password, hash_password


PRIMARY_ADMIN_NAME = "ROHIT GANGULY"
PRIMARY_ADMIN_EMAIL = "gangulyrohit2008@gmail.com"


def create_primary_admin():
    print("\n======================================")
    print("       CIVICTRACK PRIMARY ADMIN")
    print("======================================\n")

    print(f"Name:  {PRIMARY_ADMIN_NAME}")
    print(f"Email: {PRIMARY_ADMIN_EMAIL}")
    print("Role:  admin\n")

    confirmation = input(
        "Type CREATE to create this administrator account: "
    ).strip()

    if confirmation != "CREATE":
        print("\nSetup cancelled.")
        return

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Check whether this email is already registered.
        cursor.execute(
            "SELECT id, full_name, role FROM users WHERE LOWER(email) = LOWER(?)",
            (PRIMARY_ADMIN_EMAIL,)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            print("\nThis email address is already registered.")
            print(f"Existing name: {existing_user['full_name']}")
            print(f"Existing role: {existing_user['role']}")
            print(
                "\nNo account was changed. Please contact me with this "
                "result before proceeding."
            )
            return

        password = getpass.getpass("Create a password: ")
        confirm_password = getpass.getpass("Confirm the password: ")

        if password != confirm_password:
            print("\nError: Passwords do not match.")
            return

        password_valid, password_message = validate_password(password)

        if not password_valid:
            print(f"\nError: {password_message}")
            return

        password_hash = hash_password(password)

        # Create a database backup before making changes.
        database_dir = Path(__file__).resolve().parent / "database"
        backup_dir = database_dir / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"civictrack_before_admin_{timestamp}.db"

        backup_connection = sqlite3.connect(str(backup_path))
        try:
            connection.backup(backup_connection)
        finally:
            backup_connection.close()

        cursor.execute(
            """
            INSERT INTO users (
                full_name,
                email,
                password_hash,
                role,
                department_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                PRIMARY_ADMIN_NAME,
                PRIMARY_ADMIN_EMAIL,
                password_hash,
                "admin",
                None,
            )
        )

        connection.commit()

        print("\n======================================")
        print("PRIMARY ADMIN CREATED SUCCESSFULLY")
        print("======================================")
        print(f"Name: {PRIMARY_ADMIN_NAME}")
        print(f"Email: {PRIMARY_ADMIN_EMAIL}")
        print("Role: admin")
        print(f"\nDatabase backup: {backup_path}")
        print("\nYou can now test your administrator login.")

    except Exception as error:
        connection.rollback()
        print(f"\nAdministrator setup failed: {error}")

    finally:
        connection.close()


if __name__ == "__main__":
    create_primary_admin()
