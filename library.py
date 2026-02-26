import base64
import csv
import getpass
import hashlib
import json
import os
import sqlite3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MASTER_FILE = "master.json"

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
    conn = sqlite3.connect("passwords.db")
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

def view_passwords(fernet, conn):
    cursor = conn.execute('SELECT site, username, password, note note FROM passwords')
    for site, username, encrypted_password, note in cursor:
        password = decrypt(encrypted_password, fernet)
        print("Sito: {} | Username: {} | Password: {} | Note: {}".format(site, username, password, note))

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

# --- Salvataggio hash della master password ---
def setup_master_password():
    password = getpass.getpass("Scegli una master password: ")
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

    password = getpass.getpass("Inserisci master password: ")
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000).hex()

    if hashed == stored_hash:
        print("Accesso consentito!")
        return password, salt  # Possiamo usare questa password per cifrare/decriptare
    else:
        print("Password errata!")
        return None, salt