from database import get_db_connection
from werkzeug.security import generate_password_hash


def migrate_passwords():

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT user_id, password
        FROM users
        """
    )

    users = cursor.fetchall()

    updated_count = 0

    for user in users:

        current_password = user["password"]

        # Skip passwords that are already hashed
        if (
            current_password.startswith("scrypt:")
            or current_password.startswith("pbkdf2:")
        ):
            continue

        hashed_password = generate_password_hash(
            current_password
        )

        cursor.execute(
            """
            UPDATE users

            SET password = %s

            WHERE user_id = %s
            """,
            (
                hashed_password,
                user["user_id"]
            )
        )

        updated_count += 1

    connection.commit()

    cursor.close()
    connection.close()

    print(
        f"Password migration complete. "
        f"Updated {updated_count} user(s)."
    )


if __name__ == "__main__":
    migrate_passwords()