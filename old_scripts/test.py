from old_library import *

def main_sqlite3():
    master_password, salt = verify_master_password()
    key = generate_key(master_password, salt)
    fernet = Fernet(key)

    conn = init_db()

    while True:
        print("\n--- MENU ---")
        print("1. Aggiungi password")
        print("2. Visualizza password")
        print("3. Importa password da CSV")
        print("4. Esci")
        choice = input("Scegli un'opzione: ")

        if choice == "1":
            add_password(fernet, conn)
        elif choice == "2":
            view_passwords(fernet, conn)
        elif choice == "3":
            filename = input("Inserisci nome file CSV: ")
            import_csv(fernet, conn, filename)
        elif choice == "4":
            break
        else:
            print("Opzione non valida!")

    conn.close()

def main_postgres():
    master_password, salt = verify_master_password_postgres()
    key = generate_key(master_password, salt)
    fernet = Fernet(key)

    conn = init_db_postgres()

    while True:
        print("\n--- MENU ---")
        print("1. Aggiungi password")
        print("2. Visualizza password")
        print("3. Importa password da CSV")
        print("4. Esci")
        choice = input("Scegli un'opzione: ")

        if choice == "1":
            add_password_postgres(fernet, conn)
        elif choice == "2":
            view_passwords_postgres(fernet, conn)
        elif choice == "3":
            filename = input("Inserisci nome file CSV: ")
            import_csv_postgres(fernet, conn, filename)
        elif choice == "4":
            break
        else:
            print("Opzione non valida!")

    conn.close()


if __name__ == '__main__':
    main_postgres()
