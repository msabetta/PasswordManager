import os
from cryptography.fernet import Fernet

KEY_FILE = "secret.key"


def generate_key():
    """
    Genera una nuova chiave Fernet e la salva su file.
    """
    key = Fernet.generate_key()

    with open(KEY_FILE, "wb") as f:
        f.write(key)

    # Permessi sicuri (solo su sistemi Unix/Linux/Mac)
    try:
        os.chmod(KEY_FILE, 0o600)
    except:
        pass

    return key


def load_key():
    """
    Carica la chiave dal file.
    Se non esiste, la genera automaticamente.
    """
    if not os.path.exists(KEY_FILE):
        print("Chiave non trovata. Generazione nuova chiave...")
        return generate_key()

    with open(KEY_FILE, "rb") as f:
        return f.read()


def get_fernet():
    """
    Restituisce un oggetto Fernet pronto all'uso.
    """
    key = load_key()
    return Fernet(key)


if __name__ == "__main__":
    # Test rapido
    fernet = get_fernet()
    print("Chiave caricata correttamente.")