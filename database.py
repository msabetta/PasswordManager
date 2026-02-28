import os
import sqlite3
import psycopg2
from psycopg2 import sql
import csv


class DatabaseInitializer:

    def __init__(self, db_type, config=None):
        self.db_type = db_type.lower()
        self.config = config or {}
        self.conn = None

    # ======================================
    # PUBLIC METHOD
    # ======================================

    def initialize(self):
        if self.db_type == "sqlite":
            self._init_sqlite()
        elif self.db_type == "postgres":
            self._init_postgres()
        else:
            raise ValueError("Database non supportato. Usa 'sqlite' o 'postgres'.")

        return self.conn

    # ======================================
    # SQLITE
    # ======================================

    def _init_sqlite(self):
        os.makedirs("data", exist_ok=True)
        db_path = os.path.join("data", "passwords.db")

        self.conn = sqlite3.connect(db_path)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT NOT NULL,
                username TEXT NOT NULL,
                password BLOB NOT NULL,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()
        print("SQLite inizializzato correttamente.")

    # ======================================
    # POSTGRES
    # ======================================

    def _init_postgres(self):

        dbname = self.config.get("database", "personal")
        user = self.config.get("user", "postgres")
        password = self.config.get("password", "new_password")
        host = self.config.get("host", "localhost")
        port = self.config.get("port", "5432")

        # 1️⃣ Connessione al DB di sistema per creare il database se non esiste
        system_conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port
        )
        system_conn.autocommit = True
        system_cursor = system_conn.cursor()

        system_cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (dbname,)
        )

        if not system_cursor.fetchone():
            system_cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(dbname)
                )
            )
            print(f"Database PostgreSQL '{dbname}' creato.")

        system_cursor.close()
        system_conn.close()

        # 2️⃣ Connessione al database target
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )

        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id SERIAL PRIMARY KEY,
                site TEXT NOT NULL,
                username TEXT NOT NULL,
                password BYTEA NOT NULL,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()
        cursor.close()

        print("PostgreSQL inizializzato correttamente.")


# =====================================================
# DATABASE WRAPPER
# =====================================================

class Database:

    def __init__(self, db_type):
        self.db_type = db_type
        self.conn = None
        self.init_db()


    def init_db(self):

        if self.db_type == "sqlite":
            os.makedirs("data", exist_ok=True)
            self.conn = sqlite3.connect("data/passwords.db")
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password BLOB NOT NULL,
                    note TEXT
                )
            ''')

        elif self.db_type == "postgres":
            self.conn = psycopg2.connect(
                database="personal",
                user="postgres",
                password="new_password",
                host="localhost",
                port="5432"
            )
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS passwords (
                    id SERIAL PRIMARY KEY,
                    site TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password BYTEA NOT NULL,
                    note TEXT
                )
            ''')
            cursor.close()

        self.conn.commit()

    def add(self, site, username, password, note):

        if self.db_type == "sqlite":
            self.conn.execute(
                "INSERT INTO passwords (site, username, password, note) VALUES (?, ?, ?, ?)",
                (site, username, password, note)
            )
        else:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO passwords (site, username, password, note) VALUES (%s, %s, %s, %s)",
                (site, username, password, note)
            )
            cursor.close()

        self.conn.commit()

    def fetch_all(self):

        if self.db_type == "sqlite":
            cursor = self.conn.execute("SELECT site, username, password, note FROM passwords")
            return cursor.fetchall()
        else:
            cursor = self.conn.cursor()
            cursor.execute("SELECT site, username, password, note FROM passwords")
            rows = cursor.fetchall()
            cursor.close()
            return rows

    def import_csv(self, fernet, filename):

        if not os.path.exists(filename):
            print("File non trovato.")
            return

        try:
            with open(filename, newline='', encoding='utf-8') as csvfile:

                reader = csv.DictReader(csvfile)

                if not reader.fieldnames:
                    print("CSV senza intestazioni.")
                    return

                # Normalizza intestazioni
                normalized_headers = {
                    h.lower().strip(): h for h in reader.fieldnames
                }

                # Sinonimi riconosciuti
                field_map = {
                    "site": ["site", "url", "website", "domain", "link"],
                    "username": ["username", "user", "login", "email", "mail", "name"],
                    "password": ["password", "pass", "pwd"],
                    "note": ["note", "notes", "description", "comment"]
                }

                detected = {}

                for logical_field, variants in field_map.items():
                    for variant in variants:
                        if variant in normalized_headers:
                            detected[logical_field] = normalized_headers[variant]
                            break

                print("Colonne rilevate:", detected)

                if "password" not in detected:
                    print("Colonna password non trovata. Import annullato.")
                    return

                for row in reader:

                    site = row.get(detected.get("site", ""), "")
                    username = row.get(detected.get("username", ""), "")
                    password = row.get(detected.get("password", ""), "")
                    note = row.get(detected.get("note", ""), "")

                    if not password:
                        continue

                    encrypted = fernet.encrypt(password.encode())

                    if self.db_type == "sqlite":
                        self.conn.execute(
                            "INSERT INTO passwords (site, username, password, note) VALUES (?, ?, ?, ?)",
                            (site, username, encrypted, note)
                        )
                    else:
                        cursor = self.conn.cursor()
                        cursor.execute(
                            "INSERT INTO passwords (site, username, password, note) VALUES (%s, %s, %s, %s)",
                            (site, username, encrypted, note)
                        )
                        cursor.close()

                self.conn.commit()
                print("Import completato con successo.")

        except Exception as e:
            print("Errore durante import:", e)
