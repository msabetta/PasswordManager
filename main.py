from manager import *
from database import *
from menu import Menu
from crypto import *
from getpass import getpass


def main():
    db_choice = input("Scegli database (sqlite/postgres): ").lower()
    db = Database(db_choice)

    master_password, salt = verify_master_password()

    if not master_password:
        return

    key = Crypto.generate_key(master_password, salt)
    fernet = Fernet(key)

    while True:

        choice = Menu.menu()

        if choice == "1":
            site = input("Sito: ")
            username = input("Username: ")
            password = Crypto.set_password(getpass("Password: "))
            note = input("Note: ")

            encrypted = Crypto.encrypt(password, fernet)
            db.add(site, username, encrypted, note)

            print("Password salvata.")

        elif choice == "2":
            rows = db.fetch_all()

            for site, username, encrypted_password, note in rows:

                if isinstance(encrypted_password, memoryview):
                    encrypted_password = encrypted_password.tobytes()

                decrypted = Crypto.decrypt(encrypted_password, fernet)

                print("Sito: {} | Username: {} | Password: {} | Note: {}".format(site,username,decrypted,note))

        elif choice == "3":
            filename = input("Percorso file CSV: ")
            db.import_csv(fernet, filename)

        elif choice == "4":
            print("Uscita.")
            break

        else:
            print("Scelta non valida.")


if __name__ == "__main__":
    main()