import sqlite3
import hashlib
import os

class Database:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.init_db()
        return cls._instance

    def init_db(self, db_path="database/railway_testing.db"):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_tables()
        self.seed_users()  # Ensure predefined users exist

    def create_tables(self):
        """Load and execute schema.sql file to create tables."""
        try:
            with open("database/schema.sql", "r") as f:
                schema_sql = f.read()
            self.cursor.executescript(schema_sql)
            self.connection.commit()
        except Exception as e:
            print(f"Error executing schema.sql: {e}")

    def execute_query(self, query, params=()):
        """Execute an SQL query with parameters."""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def fetch_one(self, query, params=()):
        """Fetch a single row from the database."""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Database fetch error: {e}")
            return None

    def fetch_all(self, query, params=()):
        """Fetch all rows from the database."""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database fetch error: {e}")
            return []

    ### --- USER MANAGEMENT --- ###

    def hash_password(self, password):
        """Hash a password using SHA-256 for secure storage."""
        salt = os.urandom(16)  # Generate a random salt
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return salt.hex() + hashed_password.hex()  # Store salt+hash together

    def verify_password(self, stored_hash, input_password):
        """Verify a password against the stored hash."""
        salt = bytes.fromhex(stored_hash[:32])  # Extract salt
        stored_hashed = stored_hash[32:]  # Extract hashed part
        input_hashed = hashlib.pbkdf2_hmac('sha256', input_password.encode(), salt, 100000).hex()
        return stored_hashed == input_hashed

    def insert_user(self, username, password, name):
        """Insert a new user into the database with a hashed password and a dummy name."""
        if self.user_exists(username):
            return False  # User already exists

        hashed_password = self.hash_password(password)
        return self.execute_query(
            "INSERT INTO users (username, password, name) VALUES (?, ?, ?)",
            (username, hashed_password, name)
        )

    def user_exists(self, username):
        """Check if a user exists in the database."""
        return self.fetch_one("SELECT id FROM users WHERE username = ?", (username,)) is not None

    def authenticate_user(self, username, password):
        """Authenticate user login by verifying hashed password."""
        user = self.fetch_one("SELECT password FROM users WHERE username = ?", (username,))
        if user and self.verify_password(user[0], password):
            return True  # Valid credentials
        return False  # Invalid credentials

    def seed_users(self):
        """Seed the database with up to 5 predefined users, including dummy names."""
        predefined_users = [
            ("admin1", "password123", "Admin One"),
            ("admin2", "securePass", "Admin Two"),
            ("user1", "userPass1", "User One"),
            ("user2", "userPass2", "User Two"),
            ("user3", "userPass3", "User Three")
        ]

        for username, password, name in predefined_users:
            if not self.user_exists(username):
                self.insert_user(username, password, name)
                print(f"Predefined user '{username}' added with dummy name '{name}'.")

    ### --- PROJECT MANAGEMENT --- ###

    def insert_project(self, project_name, created_by):
        """Insert a new project into the database."""
        return self.execute_query("INSERT INTO projects (project_name, created_by) VALUES (?, ?)", (project_name, created_by))

    def get_projects(self):
        """Retrieve all projects from the database."""
        return self.fetch_all("SELECT * FROM projects")

    ### --- SENSOR DATA MANAGEMENT --- ###

    def insert_sensor_data(self, project_id, sensor_type, sensor_value, timestamp):
        """Insert sensor data into the database."""
        return self.execute_query(
            "INSERT INTO sensor_data (project_id, sensor_type, sensor_value, timestamp) VALUES (?, ?, ?, ?)",
            (project_id, sensor_type, sensor_value, timestamp)
        )

    def get_sensor_data(self, project_id):
        """Retrieve sensor data for a specific project."""
        return self.fetch_all("SELECT * FROM sensor_data WHERE project_id = ?", (project_id,))

    def close_connection(self):
        """Close the database connection."""
        self.connection.close()
