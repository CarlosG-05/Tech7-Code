import os
import time
import logging
import mysql.connector
from typing import Optional
from dotenv import load_dotenv
from mysql.connector import Error

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    """Custom exception for database connection failures"""
    pass

def get_db_connection(
    max_retries: int = 12,  # 12 retries = 1 minute total (12 * 5 seconds)
    retry_delay: int = 5,  # 5 seconds between retries
) -> mysql.connector.MySQLConnection:
    """Create database connection with retry mechanism."""
    connection: Optional[mysql.connector.MySQLConnection] = None
    attempt = 1
    last_error = None

    while attempt <= max_retries:
        try:
            connection = mysql.connector.connect(
                host=os.getenv("MYSQL_HOST"),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DATABASE"),
                port=int(os.getenv('MYSQL_PORT')),
                ssl_ca=os.getenv('MYSQL_SSL_CA'),  # Path to CA certificate file
                ssl_verify_identity=True
            )

            # Test the connection
            connection.ping(reconnect=True, attempts=1, delay=0)
            logger.info("Database connection established successfully")
            return connection

        except Error as err:
            last_error = err
            logger.warning(
                f"Connection attempt {attempt}/{max_retries} failed: {err}. "
                f"Retrying in {retry_delay} seconds..."
            )

            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass

            if attempt == max_retries:
                break

            time.sleep(retry_delay)
            attempt += 1

    raise DatabaseConnectionError(
        f"Failed to connect to database after {max_retries} attempts. "
        f"Last error: {last_error}"
    )

async def setup_database(initial_users: dict = None):
    """Creates user and session tables and populates initial user data if provided."""
    connection = None
    cursor = None

    # Define table schemas
    table_schemas = {
        "users": """
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                email VARCHAR(255) NOT NULL UNIQUE,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                city VARCHAR(255) NOT NULL,
                state VARCHAR(255),
                country VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "sessions": """
            CREATE TABLE sessions (
                id VARCHAR(36) PRIMARY KEY,
                user_id INT NOT NULL,
                username VARCHAR(255) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """,
        "devices": """
            CREATE TABLE devices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                devicename VARCHAR(255) NOT NULL,
                owner VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "sensor_data": """
            CREATE TABLE sensor_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                devicename VARCHAR(255) NOT NULL,
                temperature FLOAT NOT NULL,
                pressure FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "clothes": """
            CREATE TABLE clothes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                clothes VARCHAR(255) NOT NULL,
                user VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
    }

    try:
        # Get database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        # Drop and recreate tables one by one
        for table_name in ["sessions", "users", "devices", "sensor_data", "clothes"]:
            # Drop table if exists
            logger.info(f"Dropping table {table_name} if exists...")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            connection.commit()

        # Recreate tables one by one
        for table_name, create_query in table_schemas.items():

            try:
                # Create table
                logger.info(f"Creating table {table_name}...")
                cursor.execute(create_query)
                connection.commit()
                logger.info(f"Table {table_name} created successfully")

            except Error as e:
                logger.error(f"Error creating table {table_name}: {e}")
                raise

        # Insert initial users if provided
        if initial_users:
            try:
                print(initial_users)
                insert_query = "INSERT INTO users (first_name, last_name, email, username, password, city, state, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                for user in initial_users:
                    cursor.execute(insert_query, user)
                connection.commit()
                logger.info(f"Inserted {len(initial_users)} initial users")
            except Error as e:
                logger.error(f"Error inserting initial users: {e}")
                raise

    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            logger.info("Database connection closed")

async def create_user(username: str, password: str, email: str, first_name: str, last_name: str, city: str, state: str, country: str):
    """Creates user and session tables and populates initial user data if provided."""
    connection = None
    cursor = None

    try:
        # Get database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert New User
        try:
                insert_query = "INSERT INTO users (first_name, last_name, email, username, password, city, state, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (first_name, last_name, email, username, password, city, state, country))
                connection.commit()
                logger.info(f"Inserted {username} initial users")
        except Error as e:
                logger.error(f"Error inserting initial users: {e}")
                raise    

    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            logger.info("Database connection closed")

async def add_device(devicename: str, owner: str):
    """Add a new device to the database."""
    connection = None
    cursor = None

    try:
        # Get database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert New Device
        insert_query = "INSERT INTO devices (devicename, owner) VALUES (%s, %s)"
        cursor.execute(insert_query, (devicename, owner))
        connection.commit()
        logger.info(f"Inserted {devicename} device")
    except Error as e:
        logger.error(f"Error inserting device: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            logger.info("Database connection closed")

async def add_sensor_data(devicename: str, temperature: float, pressure: float):
    """Creates user and session tables and populates initial user data if provided."""
    connection = None
    cursor = None

    try:
        # Get database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert New User
        try:
                insert_query = "INSERT INTO sensor_data (devicename, temperature, pressure) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (devicename, temperature, pressure))
                connection.commit()
                logger.info(f"Inserted sensor data for {devicename}")
        except Error as e:
                logger.error(f"Error inserting sensor data: {e}")
                raise    

    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            logger.info("Database connection closed")

async def get_weather_by_device(devicename: str):
    """Retrieve the latest sensor data for a given device name."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM sensor_data 
            WHERE devicename = %s 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (devicename,))
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

async def get_devices_by_owner(owner: str):
    """Retrieve the device names for a given owner."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT devicename FROM devices 
            WHERE owner = %s 
        """, (owner,))
        result = cursor.fetchall()
        return [row['devicename'] for row in result]
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

async def get_user_by_username(username: str) -> Optional[dict]:
    """Retrieve user from database by username."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

async def get_user_by_id(user_id: int) -> Optional[dict]:
    """
    Retrieve user from database by ID.

    Args:
        user_id: The ID of the user to retrieve

    Returns:
        Optional[dict]: User data if found, None otherwise
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

async def create_session(user_id: int, session_id: str, username: str) -> bool:
    """Create a new session in the database."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO sessions (id, user_id, username) VALUES (%s, %s, %s)", (session_id, user_id, username)
        )
        connection.commit()
        return True
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

async def get_session(session_id: str) -> Optional[dict]:
    """Retrieve session from database."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT *
            FROM sessions s
            WHERE s.id = %s
        """,
            (session_id,),
        )
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

async def get_user_by_session(session_id: str) -> Optional[dict]:
    """Retrieve user from database by session ID."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT u.*
            FROM users u
            JOIN sessions s ON u.id = s.user_id
            WHERE s.id = %s
        """,
            (session_id,),
        )
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

async def add_clothes(clothes: str, user: str):
    """Add a new clothes to the database."""
    connection = None
    cursor = None

    try:
        # Get database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert New Clothes
        insert_query = "INSERT INTO clothes (clothes, user) VALUES (%s, %s)"
        cursor.execute(insert_query, (clothes, user))
        connection.commit()
        logger.info(f"Inserted {clothes} clothes")
    except Error as e:
        logger.error(f"Error inserting clothes: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            logger.info("Database connection closed")

async def get_all_clothes_by_user(user: str):
    """Retrieve the clothes for a given user."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM clothes 
            WHERE user = %s 
        """, (user,))
        result = cursor.fetchall()
        return result
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

async def delete_clothes(clothes_id: int) -> bool:
    """Delete clothes from the database."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM clothes WHERE id = %s", (clothes_id,))
        connection.commit()
        return True
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

async def delete_session(session_id: str) -> bool:
    """Delete a session from the database."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM sessions WHERE id = %s", (session_id,))
        connection.commit()
        return True
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
