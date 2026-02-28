import csv
import hashlib
import hmac
import json
import os
from getpass import getpass
from crypto import Crypto

MASTER_FILE = "master-password.json"


# =====================================================
# MASTER PASSWORD
# =====================================================

def setup_master_password():
    password = getpass("Scegli una master password: ")
    salt = Crypto.set_salt()

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100_000
    )

    with open(MASTER_FILE, "w") as f:
        json.dump({
            "salt": salt.hex(),
            "hash": hashed.hex(),
            "iterations": 100_000
        }, f)

    print("Master password salvata.")


def verify_master_password():

    if not os.path.exists(MASTER_FILE):
        setup_master_password()

    with open(MASTER_FILE, "r") as f:
        data = json.load(f)

    salt = bytes.fromhex(data["salt"])
    stored_hash = data["hash"]

    password = getpass("Inserisci la master password: ")

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100_000
    ).hex()

    if hmac.compare_digest(hashed, stored_hash):
        print("Accesso consentito.\n")
        return password, salt
    else:
        print("Password errata.")
        return None, salt
