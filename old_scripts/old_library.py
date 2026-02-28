import base64
import csv
import hashlib
import json
import os
import sqlite3

import psycopg2
from psycopg2 import sql, OperationalError
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from getpass import getpass

MASTER_FILE = "master.json.old"

# --- Funzioni di cifratura/decifratura ---
def generate_key(master_password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))

def encrypt(password, fernet):
    return fernet.encrypt(password.encode())

def decrypt(token, fernet):
    return fernet.decrypt(token).decode()

# --- Inizializza database ---
def init_db():
    conn = sqlite3.connect("../data/passwords.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY,
            site TEXT NOT NULL,
            username TEXT NOT NULL,
            password BLOB NOT NULL,
            note TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn


def create_database_postgres(dbname,user,password,host,port):
    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            dbname="postgres",  # Use the default 'postgres' database
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True  # Make sure to commit changes
        cursor = conn.cursor()

        # Check if the database exists
        cursor.execute(
            sql.SQL("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;"),
            [dbname]
        )
        exists = cursor.fetchone()

        if not exists:
            print(f"Database '{dbname}' does not exist. Creating it now...")
            cursor.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(dbname)))
            print(f"Database '{dbname}' created successfully.")
        else:
            print(f"Database '{dbname}' already exists.")

        # Close the connection
        cursor.close()
        conn.close()

    except OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def init_db_postgres():
    create_database_postgres("personal","postgres","new_password","localhost","5432")
    conn = psycopg2.connect(
        database="personal", user='postgres', password='new_password', host='localhost', port='5432'
    )
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY,
            site TEXT NOT NULL,
            username TEXT NOT NULL,
            password BYTEA NOT NULL,
            note TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        DO $$ 
        BEGIN 
            IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'passwords_id_seq') THEN
                CREATE SEQUENCE passwords_id_seq;
                ALTER TABLE passwords ALTER COLUMN id SET DEFAULT nextval('passwords_id_seq');
            END IF;
        END $$;
    ''')

    conn.commit()
    return conn


# --- Funzioni principali ---
def add_password(fernet, conn):
    site = input("Sito: ")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    encrypted_password = encrypt(password, fernet)
    note = input("Note: ")
    conn.execute('INSERT INTO passwords (site, username, password, note) VALUES (?, ?, ?, ?)',
                 (site, username, encrypted_password, note))
    conn.commit()
    print("Password salvata!")


def add_password_postgres(fernet, conn):
    site = input("Sito: ")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    encrypted_password = encrypt(password, fernet)
    note = input("Note: ")
    cursor = conn.cursor()
    cursor.execute('INSERT INTO passwords (site, username, password, note) VALUES (%s, %s, %s, %s);',
                 (site, username, encrypted_password, note))
    conn.commit()
    print("Password salvata!")

def view_passwords(fernet, conn):
    cursor = conn.execute('SELECT site, username, password, note FROM passwords;')
    for site, username, encrypted_password, note in cursor:
        encrypted_password_bytes = encrypted_password[1:10].tobytes()
        password = decrypt(encrypted_password_bytes, fernet)
        print("Sito: {} | Username: {} | Password: {} | Note: {}".format(site, username, password, note))


def view_passwords_postgres(fernet, conn):
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT site, username, password, note FROM passwords;')
        records = cursor.fetchall()

        for site, username, encrypted_password, note in records:

            # Gestione corretta dei tipi restituiti da PostgreSQL
            if isinstance(encrypted_password, memoryview):
                encrypted_password_bytes = encrypted_password.tobytes()
            elif isinstance(encrypted_password, str):
                encrypted_password_bytes = encrypted_password.encode()
            else:
                encrypted_password_bytes = encrypted_password

            # Decrittazione
            password = fernet.decrypt(encrypted_password_bytes).decode()

            print("Sito: {} | Username: {} | Password: {} | Note: {}".format(site,username,password,note))

    except Exception as e:
        print("Errore durante la lettura delle password: {}".format(e))

    finally:
        cursor.close()

def import_csv(fernet, conn, filename):
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                username = row.get('name')
                site = row.get('url')
                password = row.get('password')
                note = row.get('note')
                if site and username and password and note:
                    encrypted_password = encrypt(password, fernet)
                    conn.execute(
                        'INSERT INTO passwords (site, username, password, note) VALUES (?, ?, ?, ?)',
                        (site, username, encrypted_password, note)
                    )
            conn.commit()
        print("Importazione da {} completata!".format(filename))
    except Exception as e:
        print("Errore durante l'importazione:", e)

def import_csv_postgres(fernet, conn, filename):
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            cursor = conn.cursor()
            for row in reader:
                username = row.get('name')
                site = row.get('url')
                password = row.get('password')
                note = row.get('note')
                if site and username and password and note:
                    encrypted_password = encrypt(password, fernet)
                    cursor.execute(
                        'INSERT INTO passwords (site, username, password, note) VALUES (%s, %s, %s, %s);',
                        (site, username, encrypted_password, note)
                    )
            conn.commit()
        print("Importazione da {} completata!".format(filename))
    except Exception as e:
        print("Errore durante l'importazione:", e)

# --- Salvataggio hash della master password ---
def setup_master_password():
    #password = input("Scegli una master password: ")
    password = getpass("Scegli una master password: ")
    conn = init_db()
    salt = os.urandom(21)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
    data = {'salt': salt.hex(), 'hash': hashed.hex()}
    with open(MASTER_FILE, 'w') as f:
        json.dump(data, f)
    print("Master password salvata con successo!")

# --- Salvataggio hash della master password ---
def setup_master_password_postgres():
    #password = input("Scegli una master password: ")
    password = getpass("Scegli una master password: ")
    conn = init_db_postgres()
    salt = os.urandom(21)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
    data = {'salt': salt.hex(), 'hash': hashed.hex()}
    with open(MASTER_FILE, 'w') as f:
        json.dump(data, f)
    print("Master password salvata con successo!")


# --- Verifica master password ---
def verify_master_password():
    if not os.path.exists(MASTER_FILE):
        print("Master password non trovata. Configurazione iniziale.")
        setup_master_password()

    with open(MASTER_FILE, 'r') as f:
        data = json.load(f)
    salt = bytes.fromhex(data['salt'])
    stored_hash = data['hash']

    #password = input("Inserisci la master password: ")
    password = getpass("Scegli una master password: ")
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000).hex()

    if hashed == stored_hash:
        print("Accesso consentito!")
        return password, salt  # Possiamo usare questa password per cifrare/decriptare
    else:
        print("Password errata!")
        return None, salt


def verify_master_password_postgres():
    if not os.path.exists(MASTER_FILE):
        print("Master password non trovata. Configurazione iniziale.")
        setup_master_password_postgres()

    with open(MASTER_FILE, 'r') as f:
        data = json.load(f)
    salt = bytes.fromhex(data['salt'])
    stored_hash = data['hash']

    #password = input("Inserisci la master password: ")
    password = getpass("Scegli una master password: ")
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000).hex()

    if hashed == stored_hash:
        print("Accesso consentito!")
        return password, salt  # Possiamo usare questa password per cifrare/decriptare
    else:
        print("Password errata!")
        return None, salt